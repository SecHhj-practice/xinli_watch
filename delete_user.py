import sqlite3

username = '小佳'   # 改成你要删除的用户名

conn = sqlite3.connect('mental_health.db')
cursor = conn.cursor()

# 删除该用户的情绪记录
cursor.execute("DELETE FROM emotion_records WHERE user_id = (SELECT id FROM users WHERE username = ?)", (username,))
# 删除用户
cursor.execute("DELETE FROM users WHERE username = ?", (username,))

conn.commit()
print(f"用户 {username} 及其所有数据已删除")

# 验证
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print("剩余用户：", rows)

conn.close()