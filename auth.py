# auth.py
import hashlib
from database import get_connection, init_db, init_admin

# 初始化数据库
init_db()
init_admin()

def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, role="user"):
    """注册新用户"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True, "注册成功"
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "用户名已存在"
        return False, f"注册失败: {e}"
    finally:
        conn.close()

def login(username, password):
    """用户登录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT password, role FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row and row['password'] == hash_password(password):
        return True, row['role']
    return False, None

def get_user_id(username):
    """根据用户名获取用户ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row['id'] if row else None

def get_username_by_id(user_id):
    """根据用户ID获取用户名"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row['username'] if row else None