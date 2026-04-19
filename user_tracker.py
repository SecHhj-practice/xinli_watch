import json
from datetime import datetime
from llm_predictor import LLMPredictor
from advice_generator import AdviceGenerator
from database import get_connection
from auth import get_user_id, get_username_by_id
from collections import defaultdict

class UserTracker:
    def __init__(self):
        self.llm = LLMPredictor()
        self.advice_generator = AdviceGenerator()

    def add_real_record(self, username: str, content: str):
        """使用大模型分析情绪并保存记录"""
        user_id = get_user_id(username)
        if not user_id:
            return {"emotion": "未知", "feedback": "用户不存在", "warning": False}
        
        history = self.get_user_records(username, days=3)
        llm_result = self.llm.predict_emotion(content, history)
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emotion_records (
                user_id, content, primary_emotion, is_negative, is_crisis,
                warning_score, llm_confidence, phq9_score, gad7_score,
                key_signals, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            content,
            llm_result["primary_emotion"],
            1 if llm_result["is_negative"] else 0,
            1 if llm_result["is_crisis"] else 0,
            0.7 if llm_result["is_crisis"] else (0.5 if llm_result["is_negative"] else 0.1),
            llm_result.get("confidence", 0),
            llm_result.get("phq9_score", 0),
            llm_result.get("gad7_score", 0),
            json.dumps(llm_result.get("key_signals", [])),
            llm_result.get("recommendation", "")
        ))
        conn.commit()
        conn.close()
        
        feedback = llm_result.get("recommendation", "")
        if not feedback or len(feedback) < 5:
            feedback = self._generate_fallback_feedback(llm_result["primary_emotion"])
        
        return {
            "emotion": llm_result["primary_emotion"],
            "feedback": feedback,
            "warning": llm_result["is_crisis"]
        }
    
    def _generate_fallback_feedback(self, emotion):
        if emotion in ["快乐", "平静"]:
            return "😊 今天状态不错，继续保持～"
        elif emotion == "焦虑":
            return "🌿 感到焦虑时，试着深呼吸三次，给自己一点缓冲时间。"
        elif emotion == "悲伤":
            return "💙 辛苦了，允许自己休息一下。如果需要，可以找人聊聊。"
        elif emotion == "愤怒":
            return "🔥 情绪需要出口，试着先冷静下来，再慢慢处理。"
        else:
            return "🌸 我在这里陪着你，一切都会慢慢变好。"
    
    def get_user_records(self, username, days=None, limit=100):
        user_id = get_user_id(username)
        if not user_id:
            return []
        conn = get_connection()
        cursor = conn.cursor()
        if days:
            cursor.execute('''
                SELECT * FROM emotion_records 
                WHERE user_id = ? AND created_at >= datetime('now', ?)
                ORDER BY created_at DESC
            ''', (user_id, f'-{days} days'))
        else:
            cursor.execute('''
                SELECT * FROM emotion_records 
                WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        records = []
        for row in rows:
            record = dict(row)
            if record.get('key_signals'):
                record['key_signals'] = json.loads(record['key_signals'])
            records.append(record)
        return records
    
    def analyze_risk_rule_based(self, username):
        """基于用户记录进行规则风险分析（按天聚合后计算）"""
        user_id = get_user_id(username)
        if not user_id:
            return None
        
        conn = get_connection()
        cursor = conn.cursor()
        # 获取最近14天的记录（不限数量，因为要按天聚合）
        cursor.execute('''
            SELECT * FROM emotion_records 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) == 0:
            return None
        
        records = [dict(row) for row in rows]
        
        # ========== 按天聚合 ==========
        day_map = defaultdict(list)
        for r in records:
            date_str = r['created_at'].split()[0]  # 取日期部分
            day_map[date_str].append(r)
        
        # 获取最近14天的日期（按日期排序）
        sorted_dates = sorted(day_map.keys(), reverse=True)  # 最新在前
        recent_dates = sorted_dates[:14]
        
        daily_data = []
        for date_str in recent_dates:
            day_records = day_map[date_str]
            neg_count = sum(1 for r in day_records if r.get('is_negative', 0))
            pos_count = len(day_records) - neg_count
            is_negative_day = neg_count >= pos_count
            # 取当天主要情绪（出现最多的情绪）
            emotion_counts_day = {"快乐":0, "平静":0, "焦虑":0, "悲伤":0, "愤怒":0}
            for r in day_records:
                emo = r.get('primary_emotion', '平静')
                emotion_counts_day[emo] += 1
            primary_emotion = max(emotion_counts_day, key=emotion_counts_day.get)
            daily_data.append({
                "date": date_str,
                "is_negative_day": is_negative_day,
                "primary_emotion": primary_emotion,
                "neg_count": neg_count,
                "pos_count": pos_count,
                "records": day_records,
                "emotion_counts": emotion_counts_day
            })
        
        # 按日期升序（旧到新）以便计算连续
        daily_data_sorted = sorted(daily_data, key=lambda x: x['date'])
        total_days = len(daily_data_sorted)
        negative_days = sum(1 for d in daily_data_sorted if d['is_negative_day'])
        negative_ratio = negative_days / total_days if total_days else 0
        
        # 分两周（按天）
        week1 = daily_data_sorted[:7]
        week2 = daily_data_sorted[7:14]
        week1_neg = sum(1 for d in week1 if d['is_negative_day']) / len(week1) if week1 else 0
        week2_neg = sum(1 for d in week2 if d['is_negative_day']) / len(week2) if week2 else 0
        worsening_trend = week2_neg - week1_neg
        
        # 最近连续负面天数（从今天往前数，按天）
        recent_consecutive = 0
        for d in reversed(daily_data_sorted):  # 从最新一天开始
            if d['is_negative_day']:
                recent_consecutive += 1
            else:
                break
        
        has_crisis = any(r.get('is_crisis', 0) for r in records[-14:])  # 最近14天是否有危机
        
                # ===================== 修复：临床科学风险评分（不改动外部结构） =====================
        # 1. 取出最近14天的 PHQ-9 / GAD-7 平均分（临床核心）
        phq9_scores = [r.get('phq9_score', 0) for r in records[-14:]]
        gad7_scores = [r.get('gad7_score', 0) for r in records[-14:]]
        phq9_avg = sum(phq9_scores) / len(phq9_scores) if phq9_scores else 0
        gad7_avg = sum(gad7_scores) / len(gad7_scores) if gad7_scores else 0

        # 2. 临床标准化分数（0~1）
        phq9_norm = min(phq9_avg / 27, 1)    # 抑郁 0-27
        gad7_norm = min(gad7_avg / 21, 1)    # 焦虑 0-21
        scale_score = (phq9_norm + gad7_norm) / 2

        # 3. 新风险公式（临床权重：危机最高 > 量表 > 持续 > 趋势）
        if has_crisis:
            risk_score = 1.0  # 临床原则：有危机直接最高风险
        else:
            risk_score = (
                scale_score * 0.4 +                # 临床量表 40%（最科学）
                negative_ratio * 0.3 +             # 负面占比 30%
                min(recent_consecutive / 7, 1) * 0.2 +  # 连续负面 20%
                max(0, worsening_trend) * 0.1      # 恶化趋势 10%
            )

        # 4. 临床对齐风险等级（更合理、更严谨）
        if risk_score >= 0.75:
            risk_level = "red"
            risk_desc = "高风险"
        elif risk_score >= 0.45:
            risk_level = "yellow"
            risk_desc = "中风险"
        elif risk_score >= 0.2:
            risk_level = "blue"
            risk_desc = "低风险"
        else:
            risk_level = "green"
            risk_desc = "正常"
        # ===================== 修复结束 =====================
        
        # 情绪统计（按天的主要情绪统计）
        emotion_counts = {"快乐":0, "平静":0, "焦虑":0, "悲伤":0, "愤怒":0}
        for d in daily_data_sorted:
            emotion_counts[d['primary_emotion']] += 1
        
        daily_emotions = [(d['date'], d['primary_emotion']) for d in daily_data_sorted]
        recent_contents = [r['content'] for r in records[:3]]  # 最近3条原始内容
        
        advice = self.advice_generator.get_personalized_advice(
            user_name=username,
            emotion_counts=emotion_counts,
            metrics={
                "negative_ratio": negative_ratio * 100,
                "worsening_trend": worsening_trend * 100,
                "consecutive_bad_days": recent_consecutive,
                "crisis_days": 1 if has_crisis else 0
            },
            risk_level=risk_level,
            weekly_comparison={"week1_negative": week1_neg * 100, "week2_negative": week2_neg * 100},
            recent_contents=recent_contents
        )
        
        return {
            "user_id": username,
            "user_name": username,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_desc": risk_desc,
            "metrics": {
                "negative_ratio": round(negative_ratio * 100, 1),
                "worsening_trend": round(worsening_trend * 100, 1),
                "consecutive_bad_days": recent_consecutive,
                "crisis_days": 1 if has_crisis else 0
            },
            "emotion_counts": emotion_counts,
            "weekly_comparison": {
                "week1_negative": round(week1_neg * 100, 1),
                "week2_negative": round(week2_neg * 100, 1)
            },
            "daily_emotions": daily_emotions,
            "recent_contents": recent_contents,
            "advice": advice,
            "total_records": total_days
        }
    
    def get_all_user_reports(self):
        """获取所有用户的报告（用于管理端）"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE role = 'user'")
        users = cursor.fetchall()
        conn.close()
        
        reports = []
        for user in users:
            report = self.analyze_risk_rule_based(user['username'])
            if report:
                reports.append(report)
        reports.sort(key=lambda x: x["risk_score"], reverse=True)
        return reports