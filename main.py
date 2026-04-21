import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# ✅ PHẢI gọi load_dotenv() TRƯỚC KHI import database
load_dotenv()

from fastapi import FastAPI, Query, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import urllib.request
import urllib.parse
from sqlalchemy.orm import Session
from sqlalchemy import func

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from cedict_parser import cedict
from database import engine, Base, get_db
import models
from sentences import get_random_sentences

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo các bảng trong database (nếu chưa có)
    try:
        models.Base.metadata.create_all(bind=engine)
        print("SUCCESS: Database tables ready")
    except Exception as e:
        print(f"ERROR: Table creation failed: {e}")
    cedict.load()
    yield

app = FastAPI(
    title="汉语Go API",
    version="1.0.0",
    description="API tra từ điển CC-CEDICT & học tiếng Trung theo chuẩn HSK.",
    lifespan=lifespan,
)

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration from .env
origins = os.getenv("CORS_ORIGINS", "*").split(",")
if "*" in origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Security & Anti-Bot Middleware
@app.middleware("http")
async def security_checks(request: Request, call_next):
    ua = request.headers.get("user-agent", "").lower()
    bot_keywords = ["python-requests", "aiohttp", "curl", "wget", "headlesschrome"]
    if any(bot in ua for bot in bot_keywords):
        if "localhost" not in request.url.hostname:
            return HTTPException(status_code=403, detail="Bots not allowed").default_response

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ✅ Serve frontend tại route "/"
@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# ✅ Mount static files (CSS, JS, ảnh...)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/search")
@limiter.limit("30/minute")
def search_words(
    request: Request,
    q: str = Query("", description="Tìm kiếm bằng chữ Hán, pinyin hoặc tiếng Anh"),
    limit: int = Query(40, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    results = cedict.search(q, limit=limit, offset=offset)
    return {"query": q, "count": len(results), "results": results}


@app.get("/api/hsk/{level}")
def get_hsk_words(
    level: int,
    limit: int = Query(50, ge=1, le=300),
    offset: int = Query(0, ge=0),
):
    if level < 1 or level > 6:
        return {"error": "Level must be 1-6"}
    return cedict.get_hsk(level, limit=limit, offset=offset)



@app.post("/api/saved_words")
def save_word(
    word: str, pinyin: str, meaning: str, hsk_level: int = 0,
    db: Session = Depends(get_db)
):
    existing = db.query(models.SavedWord).filter(models.SavedWord.word == word).first()
    if existing:
        return {"msg": "Already saved", "status": "exists"}

    new_word = models.SavedWord(
        user_id=1,
        word=word,
        pinyin=pinyin,
        meaning=meaning,
        hsk_level=hsk_level
    )
    db.add(new_word)
    db.commit()
    return {"msg": "Saved", "status": "success"}


@app.get("/api/saved_words")
def get_saved_words(db: Session = Depends(get_db)):
    return db.query(models.SavedWord).order_by(models.SavedWord.id.desc()).all()


@app.delete("/api/saved_words/{word_id}")
def delete_saved_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(models.SavedWord).filter(models.SavedWord.id == word_id).first()
    if word:
        db.delete(word)
        db.commit()
        return {"status": "success"}
    return {"status": "error", "msg": "Not found"}


@app.get("/api/hsk")
def hsk_summary(db: Session = Depends(get_db)):
    summary = cedict.hsk_summary()
    db_counts = db.query(models.SavedWord.hsk_level, func.count(models.SavedWord.id))\
                  .group_by(models.SavedWord.hsk_level).all()
    db_map = {level: count for level, count in db_counts if level > 0}
    for s in summary:
        s["learned"] = db_map.get(s["level"], 0)
    return summary
@app.post("/api/hsk/update")
def update_hsk_database(background_tasks: BackgroundTasks):
    # Tải danh sách từ nhanh chóng (không dịch ngay)
    success = cedict.download_hsk_data(preload=False)
    if success:
        # Chạy việc dịch nghĩa ở background để không làm treo UI
        background_tasks.add_task(cedict.preload_hsk_words, cedict.hsk_words)
        return {"msg": "HSK database updated. Translation processing in background.", "status": "success"}
    else:
        return {"msg": "Update failed", "status": "error"}


@app.get("/api/random")
@limiter.limit("40/minute")
def random_words(
    request: Request,
    level: int = Query(0, ge=0, le=6, description="HSK level (0 = all)"),
    count: int = Query(20, ge=1, le=100),
):
    return cedict.random_words(level=level, count=count)


@app.get("/api/sentences")
@limiter.limit("40/minute")
def random_sentences(
    request: Request,
    level: int = Query(1, ge=1, le=6, description="HSK level"),
    count: int = Query(10, ge=1, le=30),
):
    sentences = get_random_sentences(level, count)
    return {"sentences": sentences, "count": len(sentences)}


@app.get("/api/lookup/{word}")
def lookup_word(word: str):
    result = cedict.lookup(word)
    if result:
        return result
    return {"error": "Not found", "word": word}

@app.get("/api/audio")
@limiter.limit("60/minute")
def get_audio(request: Request, text: str):
    url = f"https://translate.googleapis.com/translate_tts?client=gtx&ie=UTF-8&tl=zh-CN&q={urllib.parse.quote(text)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req, timeout=5)
        def iterfile():
            while chunk := response.read(8192):
                yield chunk
        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

