# emotion_model.py
import re

class EmotionAnalyzer:
    """细粒度情绪分析器 - 5维度情绪识别"""
    
    def __init__(self):
        # 各情绪维度的关键词库
        self.emotion_keywords = {
            '快乐': [
                '开心', '快乐', '高兴', '幸福', '兴奋', '满足', '期待', '希望',
                '阳光', '美好', '温暖', '充实', '自信', '加油', '棒', '好棒',
                '笑', '哈哈', '嘻嘻', '耶', '太棒了', '喜欢', '爱'
            ],
            '平静': [
                '平静', '安稳', '放松', '悠闲', '舒适', '安静', '宁静',
                '淡然', '从容', '淡定', '平和', '安稳'
            ],
            '焦虑': [
                '焦虑', '紧张', '担心', '害怕', '恐惧', '不安', '心慌', '烦躁',
                '压力', '喘不过气', '睡不着', '失眠', '噩梦', '心累', '崩溃'
            ],
            '悲伤': [
                '悲伤', '难过', '伤心', '痛苦', '绝望', '抑郁', '失落', '空虚',
                '想哭', '流泪', '心碎', '孤单', '孤独', '寂寞', '没意思'
            ],
            '愤怒': [
                '愤怒', '生气', '恼火', '烦躁', '火大', '不爽', '讨厌',
                '恨', '受不了', '忍不了', '凭什么'
            ]
        }
        
        # 情绪映射到预警权重
        self.emotion_weights = {
            '快乐': 0,
            '平静': 0.1,
            '焦虑': 0.6,
            '悲伤': 0.7,
            '愤怒': 0.5
        }
    
    def analyze(self, text):
        """分析文本的情绪维度分布"""
        text_lower = text.lower()
        
        # 统计每个情绪维度的得分
        scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[emotion] = score
        
        # 找出主要情绪（得分最高的）
        if max(scores.values()) > 0:
            primary_emotion = max(scores, key=scores.get)
            primary_score = scores[primary_emotion]
        else:
            primary_emotion = '平静'
            primary_score = 0.5
        
        # 计算预警分数
        warning_score = sum(self.emotion_weights.get(e, 0) * (scores[e] / (max(scores.values()) or 1)) 
                           for e in scores if scores[e] > 0)
        
        # 检测特定问题（用于针对性建议）
        detected_issues = []
        if any(kw in text_lower for kw in ['失眠', '睡不着', '噩梦']):
            detected_issues.append('失眠')
        if any(kw in text_lower for kw in ['压力', '焦虑', '紧张']):
            detected_issues.append('压力')
        if any(kw in text_lower for kw in ['孤独', '孤单', '寂寞']):
            detected_issues.append('孤独')
        if any(kw in text_lower for kw in ['绝望', '想死', '不想活']):
            detected_issues.append('危机')
        if any(kw in text_lower for kw in ['愤怒', '生气', '火大']):
            detected_issues.append('愤怒')
        if any(kw in text_lower for kw in ['抑郁', '难过', '伤心']):
            detected_issues.append('抑郁')
        
        # 确定预警等级
        if warning_score > 0.7 or '危机' in detected_issues:
            warning_level = 'red'
            warning_desc = '紧急预警'
        elif warning_score > 0.5:
            warning_level = 'yellow'
            warning_desc = '需要关注'
        elif warning_score > 0.3:
            warning_level = 'blue'
            warning_desc = '轻微波动'
        else:
            warning_level = 'green'
            warning_desc = '状态良好'
        
        return {
            'primary_emotion': primary_emotion,
            'primary_confidence': min(0.95, 0.5 + primary_score * 0.1),
            'emotion_scores': scores,
            'warning_score': round(warning_score, 3),
            'warning_level': warning_level,
            'warning_desc': warning_desc,
            'detected_issues': detected_issues
        }

# 测试
if __name__ == "__main__":
    analyzer = EmotionAnalyzer()
    
    test_texts = [
        "今天天气真好，和朋友出去玩，开心",
        "最近总是失眠，压力很大，焦虑得不行",
        "好难过，想哭，感觉很孤独",
        "很平静的一天，没什么特别的事"
    ]
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"文本: {text}")
        print(f"主要情绪: {result['primary_emotion']}")
        print(f"情绪分数: {result['emotion_scores']}")
        print(f"预警等级: {result['warning_desc']}")
        print(f"检测到问题: {result['detected_issues']}")
        print()