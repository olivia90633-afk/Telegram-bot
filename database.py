import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    messages INTEGER DEFAULT 0,
    premium INTEGER DEFAULT 0,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def add_user(user_id, username):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()


def increment_messages(user_id):
    cursor.execute(
        "UPDATE users SET messages = messages + 1 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()


def set_premium(user_id, value=1):
    cursor.execute(
        "UPDATE users SET premium=? WHERE user_id=?",
        (value, user_id)
    )
    conn.commit()


def stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE premium=1")
    premium = cursor.fetchone()[0]

    return total, premium
