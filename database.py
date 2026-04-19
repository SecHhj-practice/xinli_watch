# database.py
import sqlite3
import os
import hashlib  # 添加这行
from datetime import datetime

DB_PATH = "mental_health.db"

def hash_password(password):
    """密码加密（与 auth.py 保持一致）"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 情绪记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            primary_emotion TEXT NOT NULL,
            is_negative BOOLEAN DEFAULT 0,
            is_crisis BOOLEAN DEFAULT 0,
            warning_score REAL DEFAULT 0,
            llm_confidence REAL DEFAULT 0,
            phq9_score INTEGER DEFAULT 0,
            gad7_score INTEGER DEFAULT 0,
            key_signals TEXT,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON emotion_records(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON emotion_records(created_at)')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def init_admin():
    """初始化管理员账号（如果不存在）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # 使用加密密码（与 auth.py 一致）
        encrypted_password = hash_password('admin123')
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', encrypted_password, 'admin')
        )
        conn.commit()
        print("管理员账号已创建（用户名: admin, 密码: admin123）")
    
    conn.close()

# 如果直接运行此文件，初始化数据库
if __name__ == "__main__":
    init_db()
    init_admin()