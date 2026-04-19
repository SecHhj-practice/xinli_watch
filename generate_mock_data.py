# generate_mock_data.py （最终精确版）
"""
模拟数据生成脚本 - 最终版
生成三个演示账号，风险等级严格对应：
- 低风险_演示：正常/低风险（绿色/蓝色）
- 中风险_演示：中风险（黄色）
- 高风险_演示：高风险（红色）
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
import hashlib

DB_PATH = "mental_health.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user_if_not_exists(username, password="123456", role="user"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
        print(f"用户 '{username}' 已存在，ID={user_id}")
    else:
        encrypted = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, encrypted, role)
        )
        user_id = cursor.lastrowid
        print(f"创建用户 '{username}'，密码 '{password}'，ID={user_id}")
    conn.commit()
    conn.close()
    return user_id


def generate_llm_detail(emotion, is_crisis):
    if emotion == "快乐":
        phq9, gad7 = 2, 1
        signals = ["开心", "愉快"]
        rec = "享受当下的快乐时光。"
    elif emotion == "平静":
        phq9, gad7 = 4, 3
        signals = ["平静", "安稳"]
        rec = "保持平和心态。"
    elif emotion == "焦虑":
        phq9, gad7 = 12, 14
        signals = ["心慌", "紧张"]
        rec = "尝试深呼吸放松。"
    elif emotion == "悲伤":
        phq9, gad7 = 16, 10
        signals = ["难过", "低落"]
        rec = "辛苦了，找人聊聊会好一些。"
    elif emotion == "愤怒":
        phq9, gad7 = 8, 12
        signals = ["生气", "烦躁"]
        rec = "先冷静下来再处理。"
    else:
        phq9, gad7 = 5, 5
        signals = ["情绪波动"]
        rec = "关注自己的情绪变化。"

    if is_crisis:
        phq9 = max(phq9, 22)
        signals = ["绝望", "不想活"]
        rec = "请立即寻求专业帮助！"

    return {
        "confidence": 0.9,
        "phq9_score": phq9,
        "gad7_score": gad7,
        "key_signals": signals,
        "recommendation": rec
    }


def insert_record(user_id, content, emotion, created_at, is_crisis=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    is_negative = emotion in ["焦虑", "悲伤", "愤怒"]
    warning_score = 0.7 if is_crisis else (0.5 if is_negative else 0.1)
    llm_detail = generate_llm_detail(emotion, is_crisis)

    cursor.execute('''
        INSERT INTO emotion_records (
            user_id, content, primary_emotion, is_negative, is_crisis,
            warning_score, llm_confidence, phq9_score, gad7_score,
            key_signals, recommendation, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, content, emotion,
        1 if is_negative else 0,
        1 if is_crisis else 0,
        warning_score,
        llm_detail["confidence"],
        llm_detail["phq9_score"],
        llm_detail["gad7_score"],
        json.dumps(llm_detail["key_signals"], ensure_ascii=False),
        llm_detail["recommendation"],
        created_at.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def generate_fixed_records(user_id, profile):
    """
    固定情绪序列，确保风险等级准确
    """
    # 固定基准日期：2026年4月17日（今天），我们以此为最新一天
    # 这样无论何时运行，生成的相对日期都是固定的
    base_date = datetime(2026, 4, 17, 20, 0, 0)

    if profile == "low":
        # 14天中只有2天轻微焦虑，其余快乐/平静
        emotions = ["快乐", "平静", "快乐", "快乐", "平静", "快乐", "平静",
                    "快乐", "快乐", "平静", "焦虑", "快乐", "平静", "快乐"]
        crisis_flags = [False] * 14
        contents = [
            "今天心情很好", "平淡的一天", "工作顺利很开心", "和朋友聚餐",
            "安静看书", "天气好心情好", "悠闲散步", "完成项目有成就感",
            "收到礼物超开心", "喝杯咖啡放松", "有点小担心", "很快恢复了",
            "听听音乐", "期待明天"
        ]
    elif profile == "medium":
        # 第一周波动，第二周恶化，最后4天连续负面，无危机
        emotions = ["平静", "焦虑", "快乐", "悲伤", "平静", "愤怒", "快乐",
                    "焦虑", "悲伤", "愤怒", "焦虑", "悲伤", "愤怒", "焦虑"]
        crisis_flags = [False] * 14
        contents = [
            "一切如常", "有点担心工作", "今天挺开心", "突然难过",
            "恢复平静", "被气到了", "和朋友聊天好转", "压力大失眠",
            "情绪低落", "很烦躁", "心慌紧张", "想哭",
            "又生气了", "焦虑不安"
        ]
    else:  # high
        # 前7天：负面为主（第5天平静），后7天：全部负面且带危机信号
        # 确保连续负面天数 ≥ 7，恶化趋势为正（第二周比第一周更差）
        emotions = [
            # 第一周（4月4日~4月10日）: 负面为主，第5天（4月8日）平静
            "焦虑", "愤怒", "悲伤", "焦虑", "平静", "愤怒", "悲伤",
            # 第二周（4月11日~4月17日）: 全部负面，且带危机
            "焦虑", "悲伤", "愤怒", "悲伤", "焦虑", "悲伤", "愤怒"
        ]
        # 后7天全部为危机信号
        crisis_flags = [False] * 7 + [True] * 7
        contents = [
            # 第一周
            "失眠心慌", "火大烦躁", "难过想哭", "持续焦虑", "稍微缓一下",
            "又生气了", "低落绝望",
            # 第二周（危机）
            "整夜睡不着", "感觉活着没意思", "崩溃大哭", "不想活了",
            "没人理解我", "撑不下去了", "没有希望了"
        ]

    # 从最新一天（i=13）向前插入
    for i in range(14):
        date = base_date - timedelta(days=13 - i)
        # 加一点分钟随机
        date = date.replace(minute=random.randint(0, 30))
        insert_record(user_id, contents[i], emotions[i], date, is_crisis=crisis_flags[i])

    print(f"已为 user_id={user_id} 生成14条记录（风险画像：{profile}）")


def main():
    print("=== 开始生成模拟数据（最终精确版） ===")

    # 先删除三个演示用户（如果存在），确保完全重置
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for uname in ["低风险_演示", "中风险_演示", "高风险_演示"]:
        cursor.execute("SELECT id FROM users WHERE username = ?", (uname,))
        row = cursor.fetchone()
        if row:
            uid = row[0]
            cursor.execute("DELETE FROM emotion_records WHERE user_id = ?", (uid,))
            cursor.execute("DELETE FROM users WHERE id = ?", (uid,))
            print(f"已删除旧用户 {uname} 及其记录。")
    conn.commit()
    conn.close()

    user_low = create_user_if_not_exists("低风险_演示", "123456")
    user_medium = create_user_if_not_exists("中风险_演示", "123456")
    user_high = create_user_if_not_exists("高风险_演示", "123456")

    generate_fixed_records(user_low, "low")
    generate_fixed_records(user_medium, "medium")
    generate_fixed_records(user_high, "high")

    print("\n=== 模拟数据生成完毕 ===")
    print("可登录账号：")
    print("  低风险_演示 / 123456  (风险等级：正常/低风险)")
    print("  中风险_演示 / 123456  (风险等级：中风险)")
    print("  高风险_演示 / 123456  (风险等级：高风险)")


if __name__ == "__main__":
    main()