# auto_tracker.py
import pandas as pd
import random
from datetime import datetime, timedelta
from emotion_model import EmotionAnalyzer
from advice_generator import AdviceGenerator

class SocialMediaAutoTracker:
    """多用户自动追踪智能体"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.advice_generator = AdviceGenerator()
        
        # 所有用户的追踪数据
        self.users_data = {}
        
        # 模拟用户画像（不同用户有不同的情绪倾向）
        self.user_profiles = {
            'user_001': {
                'name': '小明',
                'base_emotions': {'焦虑': 0.5, '悲伤': 0.3, '愤怒': 0.1, '平静': 0.05, '快乐': 0.05},
                'variance': 0.2,
                'crisis_risk': 0.1
            },
            'user_002': {
                'name': '小红',
                'base_emotions': {'快乐': 0.5, '平静': 0.3, '焦虑': 0.1, '悲伤': 0.05, '愤怒': 0.05},
                'variance': 0.2,
                'crisis_risk': 0.02
            },
            'user_003': {
                'name': '小华',
                'base_emotions': {'悲伤': 0.4, '焦虑': 0.3, '平静': 0.15, '愤怒': 0.1, '快乐': 0.05},
                'variance': 0.25,
                'crisis_risk': 0.15
            },
            'user_004': {
                'name': '小丽',
                'base_emotions': {'愤怒': 0.4, '焦虑': 0.3, '悲伤': 0.15, '平静': 0.1, '快乐': 0.05},
                'variance': 0.2,
                'crisis_risk': 0.08
            },
            'user_005': {
                'name': '小强',
                'base_emotions': {'平静': 0.5, '快乐': 0.3, '焦虑': 0.1, '悲伤': 0.05, '愤怒': 0.05},
                'variance': 0.15,
                'crisis_risk': 0.01
            }
        }
        
        # 内容模板
        self.content_templates = {
            '快乐': [
                "今天天气真好，心情不错 #日常",
                "和朋友聚餐很开心，聊了很多 #生活",
                "工作完成，轻松的一天 #加油",
                "运动了一下，出汗的感觉真好 #健康",
                "看了喜欢的电影，推荐给大家 #观影"
            ],
            '平静': [
                "今天没什么特别的事，平平淡淡 #日常",
                "安静地看了一本书 #阅读",
                "天气不错，适合发呆 #悠闲",
                "泡了杯茶，慢慢喝 #生活"
            ],
            '焦虑': [
                "最近总是失眠，压力很大 #焦虑",
                "焦虑得不行，心慌 #求助",
                "又失眠了，整晚睡不着 #痛苦",
                "心跳好快，好紧张 #焦虑",
                "脑子里全是事，停不下来 #压力"
            ],
            '悲伤': [
                "好绝望，想哭 #难过",
                "感觉活着好累 #抑郁",
                "不知道为什么，就是很难过 #心情",
                "不想说话，不想见人 #自闭",
                "好孤独，没人理解 #孤独"
            ],
            '愤怒': [
                "气死了，凭什么 #愤怒",
                "太烦了，忍不了 #火大",
                "真受不了 #吐槽",
                "什么人啊，太生气了 #愤怒"
            ]
        }
    
    def auto_collect_for_user(self, user_id, days=14):
        """自动收集单个用户的社交媒体内容"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return []
        
        records = []
        today = datetime.now()
        
        for i in range(days - 1, -1, -1):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # 根据用户画像决定当天的情绪分布
            emotion_weights = profile['base_emotions'].copy()
            # 加入随机波动
            for emotion in emotion_weights:
                variance = random.uniform(-profile['variance'], profile['variance'])
                emotion_weights[emotion] = max(0, min(1, emotion_weights[emotion] + variance))
            
            # 归一化
            total = sum(emotion_weights.values())
            if total > 0:
                emotion_weights = {k: v/total for k, v in emotion_weights.items()}
            
            # 根据权重选择情绪
            emotions = list(emotion_weights.keys())
            weights = list(emotion_weights.values())
            selected_emotion = random.choices(emotions, weights=weights)[0]
            
            # 选择对应内容
            content = random.choice(self.content_templates[selected_emotion])
            
            # 特殊：危机情况（极小概率）
            if random.random() < profile['crisis_risk']:
                content = "好绝望，不想活了 #崩溃"
                selected_emotion = '悲伤'
            
            # 情绪分析
            emotion_result = self.emotion_analyzer.analyze(content)
            
            records.append({
                'date': date,
                'user_id': user_id,
                'user_name': profile['name'],
                'content': content,
                'emotion_result': emotion_result,
                'primary_emotion': emotion_result['primary_emotion'],
                'warning_level': emotion_result['warning_level'],
                'warning_score': emotion_result['warning_score']
            })
        
        self.users_data[user_id] = records
        return records
    
    def auto_collect_all_users(self, days=14):
        """自动收集所有用户的社交媒体内容"""
        for user_id in self.user_profiles:
            self.auto_collect_for_user(user_id, days)
        
        return self.users_data
    
    def get_user_report(self, user_id, days=14):
        """获取单个用户的情绪报告"""
        if user_id not in self.users_data:
            return None
        
        records = self.users_data[user_id][-days:]
        
        if not records:
            return None
        
        # 统计各情绪出现次数
        emotion_counts = {'快乐': 0, '平静': 0, '焦虑': 0, '悲伤': 0, '愤怒': 0}
        warning_counts = {'red': 0, 'yellow': 0, 'blue': 0, 'green': 0}
        
        daily_warning_scores = []
        daily_primary_emotions = []
        
        for r in records:
            emotion_counts[r['primary_emotion']] += 1
            warning_counts[r['warning_level']] += 1
            daily_warning_scores.append(r['warning_score'])
            daily_primary_emotions.append(r['primary_emotion'])
        
        total = len(records)
        
        # 计算整体预警分数（最近一周权重更高）
        if len(daily_warning_scores) >= 7:
            recent_week = daily_warning_scores[-7:]
            overall_score = sum(recent_week) / len(recent_week)
        else:
            overall_score = sum(daily_warning_scores) / total if total > 0 else 0
        
        # 趋势分析（最近3天 vs 之前）
        if len(daily_warning_scores) >= 6:
            recent_3 = daily_warning_scores[-3:]
            previous_3 = daily_warning_scores[-6:-3]
            trend = sum(recent_3)/3 - sum(previous_3)/3
        else:
            trend = 0
        
        # 连续恶化天数
        consecutive_bad = 0
        for score in reversed(daily_warning_scores):
            if score > 0.4:
                consecutive_bad += 1
            else:
                break
        
        # 整体风险判断
        if overall_score > 0.7 or consecutive_bad >= 5:
            risk_level = 'red'
            risk_desc = '高风险'
        elif overall_score > 0.5 or trend > 0.2:
            risk_level = 'yellow'
            risk_desc = '中风险'
        elif overall_score > 0.3:
            risk_level = 'blue'
            risk_desc = '低风险'
        else:
            risk_level = 'green'
            risk_desc = '正常'
        
        # 生成个性化建议
        recent_texts = [r['content'] for r in records[-7:]]
        combined_text = ' '.join(recent_texts)
        last_emotion = self.emotion_analyzer.analyze(combined_text)
        advice = self.advice_generator.get_advice(last_emotion, combined_text)
        
        return {
            'user_id': user_id,
            'user_name': self.user_profiles[user_id]['name'],
            'total_days': len(records),
            'emotion_counts': emotion_counts,
            'warning_counts': warning_counts,
            'daily_warning_scores': daily_warning_scores,
            'daily_primary_emotions': daily_primary_emotions,
            'dates': [r['date'] for r in records],
            'records': records,
            'overall_score': round(overall_score, 3),
            'risk_level': risk_level,
            'risk_desc': risk_desc,
            'trend': round(trend, 3),
            'consecutive_bad': consecutive_bad,
            'advice': advice
        }
    
    def get_all_reports(self, days=14):
        """获取所有用户的报告"""
        reports = []
        for user_id in self.user_profiles:
            report = self.get_user_report(user_id, days)
            if report:
                reports.append(report)
        
        # 按风险等级排序（高风险优先）
        risk_order = {'red': 0, 'yellow': 1, 'blue': 2, 'green': 3}
        reports.sort(key=lambda x: risk_order.get(x['risk_level'], 4))
        
        return reports
    
    def get_high_risk_users(self, threshold=0.4):
        """筛选高风险用户"""
        high_risk = []
        for report in self.get_all_reports():
            if report['risk_level'] in ['red', 'yellow'] or report['overall_score'] > threshold:
                high_risk.append(report)
        return high_risk

# 测试
if __name__ == "__main__":
    tracker = SocialMediaAutoTracker()
    tracker.auto_collect_all_users(14)
    
    print("=== 所有用户报告 ===\n")
    for report in tracker.get_all_reports():
        print(f"{report['user_name']}: {report['risk_desc']} (分数: {report['overall_score']})")
        print(f"  情绪分布: {report['emotion_counts']}")
        print()
    
    print("=== 高风险用户 ===\n")
    for user in tracker.get_high_risk_users():
        print(f"{user['user_name']}: {user['risk_desc']} - {user['advice'][:100]}...")