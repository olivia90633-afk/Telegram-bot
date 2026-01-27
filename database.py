import sqlite3
from datetime import datetime, timedelta

DB_NAME = "ola_ai.db"  # SQLite DB file


# ======================
# INITIALIZE DATABASE
# ======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # USERS TABLE
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_paid INTEGER DEFAULT 0,
            plan TEXT,
            expires_at TEXT,
            messages_sent INTEGER DEFAULT 0,
            last_active TEXT
        )
        """
    )

    # PAYMENTS TABLE
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            amount INTEGER,
            paid_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """
    )

    conn.commit()
    conn.close()


# ======================
# USER HELPERS
# ======================
def add_or_get_user(user_id, username="Unknown"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if user is None:
        c.execute(
            "INSERT INTO users (user_id, username, last_active) VALUES (?, ?, ?)",
            (user_id, username, datetime.utcnow().isoformat()),
        )
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = c.fetchone()
    conn.close()
    return user


def increment_messages(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET messages_sent = messages_sent + 1, last_active=? WHERE user_id=?",
        (datetime.utcnow().isoformat(), user_id),
    )
    conn.commit()
    conn.close()


def set_paid(user_id, plan, duration_days):
    expires = datetime.utcnow() + timedelta(days=duration_days)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET is_paid=1, plan=?, expires_at=? WHERE user_id=?",
        (plan, expires.isoformat(), user_id),
    )
    conn.commit()
    conn.close()


def revoke_paid(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET is_paid=0, plan=NULL, expires_at=NULL WHERE user_id=?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def check_expiry(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_paid, expires_at FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()

    if result is None:
        return False
    is_paid, expires_at = result
    if not is_paid:
        return False
    if expires_at is None:
        return True
    if datetime.utcnow() > datetime.fromisoformat(expires_at):
        revoke_paid(user_id)
        return False
    return True


# ======================
# PAYMENT LOG
# ======================
def add_payment(user_id, plan, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO payments (user_id, plan, amount, paid_at) VALUES (?, ?, ?, ?)",
        (user_id, plan, amount, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


# ======================
# GET STATS (FOR DASHBOARD)
# ======================
def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return users


def get_paid_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE is_paid=1")
    users = c.fetchall()
    conn.close()
    return users


def get_revenue():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM payments")
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0


# ======================
# INIT ON IMPORT
# ======================
init_db()
