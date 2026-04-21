# Sample sentences for typing practice by HSK level
# Format: {"zh": "Chinese", "pinyin": "pinyin with tones", "vi": "Vietnamese translation", "level": 1-6}

SENTENCES = [
    # HSK 1
    {"zh": "我叫李明。", "pinyin": "wo3 jiao4 li3 ming2", "vi": "Tôi tên là Lý Minh.", "level": 1},
    {"zh": "你好吗？", "pinyin": "ni3 hao3 ma5", "vi": "Bạn khỏe không?", "level": 1},
    {"zh": "今天天气很好。", "pinyin": "jin1 tian1 tian1 qi4 hen3 hao3", "vi": "Hôm nay thời tiết rất tốt.", "level": 1},
    {"zh": "这是我的书。", "pinyin": "zhe4 shi4 wo3 de5 shu1", "vi": "Đây là quyển sách của tôi.", "level": 1},
    {"zh": "你在做什么？", "pinyin": "ni3 zai4 zuo4 shen2 me5", "vi": "Bạn đang làm gì?", "level": 1},
    {"zh": "我很高兴。", "pinyin": "wo3 hen3 gao1 xing4", "vi": "Tôi rất vui.", "level": 1},
    {"zh": "他是我的朋友。", "pinyin": "ta1 shi4 wo3 de5 peng2 you5", "vi": "Anh ấy là bạn của tôi.", "level": 1},
    {"zh": "我喜欢学习中文。", "pinyin": "wo3 xi3 huan5 xue2 xi2 zhong1 wen2", "vi": "Tôi thích học tiếng Trung.", "level": 1},

    # HSK 2
    {"zh": "我昨天去了公园。", "pinyin": "wo3 zuo2 tian1 qu4 le5 gong1 yuan2", "vi": "Hôm qua tôi đã đi công viên.", "level": 2},
    {"zh": "这个电影很有意思。", "pinyin": "zhe4 ge5 dian4 ying3 hen3 you3 yi4 si4", "vi": "Bộ phim này rất thú vị.", "level": 2},
    {"zh": "你能帮我一个忙吗？", "pinyin": "ni3 neng2 bang1 wo3 yi2 ge5 mang2 ma5", "vi": "Bạn có thể giúp tôi một việc không?", "level": 2},
    {"zh": "我想学一门新的技能。", "pinyin": "wo3 xiang3 xue2 yi2 men2 xin1 de5 ji4 neng2", "vi": "Tôi muốn học một kỹ năng mới.", "level": 2},
    {"zh": "这家餐厅的饭很好吃。", "pinyin": "zhe4 jia1 can1 ting1 de5 fan4 hen3 hao3 chi1", "vi": "Nhà hàng này có cơm rất ngon.", "level": 2},

    # HSK 3
    {"zh": "我一直想去中国旅游。", "pinyin": "wo3 yi2 zhi2 xiang3 qu4 zhong1 guo2 lv3 you2", "vi": "Tôi lâu nay muốn đi du lịch Trung Quốc.", "level": 3},
    {"zh": "虽然工作很累，但是我喜欢这份工作。", "pinyin": "sui1 ran2 gong1 zuo4 hen3 lei4 dan4 shi4 wo3 xi3 huan5 zhe4 fen4 gong1 zuo4", "vi": "Dù công việc rất mệt, nhưng tôi thích công việc này.", "level": 3},
    {"zh": "为了提高我的语言能力，我决定出国留学。", "pinyin": "wei4 le5 ti2 gao1 wo3 de5 yu3 yan2 neng2 li4 wo3 jue2 ding4 chu1 guo2 liu2 xue2", "vi": "Để nâng cao khả năng ngôn ngữ, tôi quyết định đi du học nước ngoài.", "level": 3},

    # HSK 4
    {"zh": "随着科技的发展，人们的生活方式发生了很大的变化。", "pinyin": "sui2 zhe3 ke1 ji4 de5 fa1 zhan3 ren2 men5 de5 sheng1 huo2 fang1 shi4 fa1 sheng1 le5 hen3 da4 de5 bian4 hua4", "vi": "Cùng với sự phát triển của công nghệ, lối sống của con người đã thay đổi rất nhiều.", "level": 4},
    {"zh": "我认为这是一个很好的机会，不应该错过。", "pinyin": "wo3 ren4 wei2 zhe4 shi4 yi2 ge5 hen3 hao3 de5 ji1 hui4 bu4 ying1 gai1 cuo4 guo4", "vi": "Tôi cho rằng đây là một cơ hội rất tốt, không nên bỏ lỡ.", "level": 4},

    # HSK 5
    {"zh": "关于这个问题的解决方案，我们应该进行深入的讨论。", "pinyin": "guan1 yu2 zhe4 ge5 wen4 ti2 de5 jie3 jue2 fang1 an4 wo3 men5 ying1 gai1 jin4 xing2 shen1 ru4 de5 tao3 lun4", "vi": "Về phương án giải quyết vấn đề này, chúng ta nên tiến hành thảo luận sâu sắc.", "level": 5},
]


def get_random_sentences(level: int, count: int = 10) -> list:
    """Get random sentences from a specific HSK level"""
    import random
    
    # Filter sentences by level
    level_sentences = [s for s in SENTENCES if s["level"] == level]
    
    # If not enough sentences, pad with lower level sentences
    if len(level_sentences) < count:
        all_sentences = [s for s in SENTENCES if s["level"] <= level]
        if len(all_sentences) < count:
            return all_sentences[:count]
        return random.sample(all_sentences, count)
    
    return random.sample(level_sentences, min(count, len(level_sentences)))
