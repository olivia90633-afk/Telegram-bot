import os
import sqlite3
import random
import asyncio
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

from openai import OpenAI

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ADMIN_ID = 7926402001
DB_FILE = "users.db"

client = OpenAI(api_key=OPENAI_API_KEY)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            message_count INTEGER DEFAULT 0,
            is_paid INTEGER DEFAULT 0,
            expiry TEXT,
            plan TEXT,
            revenue INTEGER DEFAULT 0,
            reminded INTEGER DEFAULT 0,
            last_seen TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_user(user_id):
    if not get_user(user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (user_id, last_seen) VALUES (?, ?)",
            (user_id, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

def increment_message(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET message_count = message_count + 1, last_seen=? WHERE user_id=?",
        (datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

def set_paid(user_id, plan, days, amount):
    expiry = datetime.utcnow() + timedelta(days=days)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE users SET
        is_paid=1,
        expiry=?,
        plan=?,
        revenue=revenue+?,
        reminded=0
        WHERE user_id=?
    """, (expiry.isoformat(), plan, amount, user_id))
    conn.commit()
    conn.close()

def revoke_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET is_paid=0, expiry=NULL, plan=NULL WHERE user_id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_paid_users(full=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if full:
        c.execute("SELECT user_id, expiry, reminded FROM users WHERE is_paid=1")
    else:
        c.execute("SELECT user_id, expiry FROM users WHERE is_paid=1")
    rows = c.fetchall()
    conn.close()
    return rows

# ================= MESSAGES =================
FREE_MESSAGES = [
    "Cashflow beats salary every time 💼📈",
    "Money follows discipline, not wishes 💰",
    "Wealth is built by systems, not luck 🔥",
    "People escape poverty by learning skills 🧠",
    "Trading done right creates freedom 🚀",
    "Smart money moves silently 💎",
    "Rich people think in probabilities 📊",
    "Money respects patience ⏳",
    "Discipline creates wealth 🛡️",
    "Skills pay forever 💼",
    "Trading rewards calm minds 🧘",
    "You don’t chase money, you attract it 🧲",
    "Consistency beats motivation 🔁",
    "Every wealthy person followed a system 📈",
    "Learning changes income 💡",
    "Risk control is power 🛡️",
    "Smart decisions compound 💎",
    "Money loves clarity 🎯",
    "Wealth is intentional 💰",
    "Focus creates fortune 🔥"
]

DAILY_TIPS = [  # 20 tips (as you requested)
    "Never trade emotionally. Calm decisions grow accounts 📊",
    "Protect capital first. Profit comes second 🛡️",
    "One asset mastery beats ten assets confusion 🎯",
    "Stop trading after 2 losses. Discipline saves money 💼",
    "Trade higher timeframes for clarity ⏱️",
    "Never increase lot size after a loss 🚫",
    "Trading is patience, not speed ⏳",
    "Consistency builds wealth 🔁",
    "Journal every trade 📒",
    "Wait for confirmation before entry 📈",
    "Avoid revenge trading 🧠",
    "Price action leads indicators 📊",
    "Your mindset is your edge 💎",
    "Losses are tuition 📚",
    "No setup, no trade ❌",
    "Rules make traders rich 💼",
    "Calm traders survive 🧘",
    "Risk 2–5% max 🛡️",
    "Discipline compounds 💰",
    "Systems create freedom 🚀"
]

SYSTEM_PROMPT = """
You are Ola AI, a professional trading mentor.
You ONLY teach IQ Option trading, money discipline, risk management, and wealth mindset.
Be human, serious, encouraging, and intelligent.
Never repeat phrases.
"""

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    add_user(uid)
    await update.message.reply_text(
        "🔥 Ola AI\n\nDo you want to start making serious money and escape poverty?\n\nReply YES 💼💰"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 SUBSCRIPTION PLANS 💎\n\n"
        "🔥 ₦2,000 → 2 Days\n"
        "💎 ₦6,000 → 1 Week\n"
        "💰 ₦25,000 → 1 Month\n"
        "👑 ₦100,000 → Lifetime\n\n"
        "━━━━━━━━━━━━━━\n"
        "🏦 Bank: Kuda Bank\n"
        "👤 Name: Olaotan Olamide\n"
        "🔢 Account No: 2082773155\n"
        "━━━━━━━━━━━━━━\n\n"
        "After payment, type /paid 💰"
    )

async def paid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Payment notice received 💸\n⏳ Admin will confirm shortly."
    )
    await context.bot.send_message(
        ADMIN_ID,
        f"💰 PAYMENT NOTICE\nUser ID: `{update.effective_user.id}`",
        parse_mode="Markdown"
    )

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "🔥 ADMIN DASHBOARD 🔥\n\n"
        "/confirm <user_id> <2d|1w|1m|life>\n"
        "/revoke <user_id>\n"
        "/stats\n"
        "/broadcast <msg>\n"
        "/expirelist\n"
        "/topusers\n"
        "/sendtip"
    )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /confirm <user_id> <plan>")
        return

    uid = int(context.args[0])
    plan = context.args[1]

    plans = {
        "2d": (2, 2000),
        "1w": (7, 6000),
        "1m": (30, 25000),
        "life": (36500, 100000)
    }

    if plan not in plans:
        await update.message.reply_text("Invalid plan.")
        return

    days, amount = plans[plan]
    set_paid(uid, plan, days, amount)

    await update.message.reply_text("✅ User confirmed.")
    await context.bot.send_message(uid, "💎 Subscription confirmed. Welcome to wealth mentorship 🤑")

async def revoke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    revoke_user(uid)
    await update.message.reply_text("❌ User revoked.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_paid=1")
    paid = c.fetchone()[0]
    c.execute("SELECT SUM(revenue) FROM users")
    revenue = c.fetchone()[0] or 0
    conn.close()

    await update.message.reply_text(
        f"📊 STATS\n\nUsers: {total}\nPaid: {paid}\nRevenue: ₦{revenue}"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    for uid in get_all_users():
        try:
            await context.bot.send_message(uid, msg)
        except:
            pass
    await update.message.reply_text("📢 Broadcast sent.")

async def sendtip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    tip = random.choice(DAILY_TIPS)
    sent = 0
    for uid, expiry in get_paid_users():
        if expiry and datetime.fromisoformat(expiry) > datetime.utcnow():
            try:
                await context.bot.send_message(uid, f"💎 Premium Tip\n\n{tip}")
                sent += 1
            except:
                pass
    await update.message.reply_text(f"✅ Tip sent to {sent} users.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    add_user(uid)
    increment_message(uid)

    user = get_user(uid)
    is_paid = user[2]
    expiry = user[3]

    if is_paid and expiry and datetime.fromisoformat(expiry) > datetime.utcnow():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": update.message.text}
            ]
        )
        await update.message.reply_text(response.choices[0].message.content)
    else:
        await update.message.reply_text(random.choice(FREE_MESSAGES))

# ================= MAIN =================
async def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("paid", paid_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("confirm", confirm))
    app.add_handler(CommandHandler("revoke", revoke))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("sendtip", sendtip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
