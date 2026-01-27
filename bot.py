import os
import random
from datetime import datetime, timedelta
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7926402001  # Your Telegram numeric ID
FREE_LIMIT = 5  # Number of free messages before subscription

DB_NAME = "ola_ai.db"

# ======================
# DATABASE FUNCTIONS
# ======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_paid INTEGER DEFAULT 0,
            plan TEXT,
            expires_at TEXT,
            messages_sent INTEGER DEFAULT 0,
            last_active TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            amount INTEGER,
            paid_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

def add_or_get_user(user_id, username="Unknown"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute(
            "INSERT INTO users (user_id, username, last_active) VALUES (?, ?, ?)",
            (user_id, username, datetime.utcnow().isoformat())
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
        (datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()

def set_paid(user_id, plan, duration_days, amount):
    expires = datetime.utcnow() + timedelta(days=duration_days)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET is_paid=1, plan=?, expires_at=? WHERE user_id=?",
        (plan, expires.isoformat(), user_id)
    )
    c.execute(
        "INSERT INTO payments (user_id, plan, amount, paid_at) VALUES (?, ?, ?, ?)",
        (user_id, plan, amount, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def revoke_paid(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET is_paid=0, plan=NULL, expires_at=NULL WHERE user_id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def check_expiry(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT is_paid, expires_at FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    if not result:
        return False
    is_paid, expires_at = result
    if not is_paid:
        return False
    if expires_at and datetime.utcnow() > datetime.fromisoformat(expires_at):
        revoke_paid(user_id)
        return False
    return True

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
# PRESET MESSAGES
# ======================
FREE_MESSAGES = [
    "Money doesn’t respond to wishes — it responds to strategy 💼📊",
    "Most people work hard, few people work smart 💡💰",
    "Salary keeps you busy, systems make you wealthy 📈",
    "The rich don’t chase money, they build value 💎",
    "There’s a reason some escape poverty — they learn different rules 🧠",
    "Real money is predictable when you understand leverage 🚀",
    "You don’t need luck to be rich, you need structure 🏗️",
    "Poverty is expensive. Wealth requires discipline 💼",
    "People who win financially think long-term, not urgent ⏳",
    "Money grows faster when emotions are removed 📊",
]

GATED_MESSAGES = [
    "I can guide you properly, but only serious ones continue 💼",
    "Serious income systems require commitment 🔐",
    "Guidance must be structured, not random 📈",
    "Once access is unlocked, I’ll break things down step by step 💎",
    "Wealth blueprints are protected for a reason 🔒",
    "You’re asking the right questions — now commitment matters 💼",
]

PREMIUM_MESSAGES = [
    "Welcome to premium guidance 💼🔥",
    "First rule: control income before increasing lifestyle 📊",
    "Money respects structure. Let’s build yours properly 🏗️",
    "From here, we focus on skills, leverage, and systems 📈",
    "This is where transformation actually starts 🚀",
]

user_used_msgs = {}  # to track sent messages

def get_unique_message(user_id, pool):
    used = user_used_msgs.get(user_id, set())
    available = [m for m in pool if m not in used]
    if not available:
        used.clear()
        available = pool[:]
    msg = random.choice(available)
    used.add(msg)
    user_used_msgs[user_id] = used
    return msg

# ======================
# BOT COMMANDS
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    add_or_get_user(user_id, username)
    await update.message.reply_text(
        "🔥 *Ola AI*\n\n"
        "Do you want to start making serious money and escape poverty?\n\n"
        "Reply *YES* 💼💰",
        parse_mode="Markdown"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 *SUBSCRIPTION PLANS* 💎\n\n"
        "🔥 ₦2,000 → 2 Days\n"
        "💎 ₦6,000 → 1 Week\n"
        "💰 ₦25,000 → 1 Month\n"
        "👑 ₦100,000 → Lifetime\n\n"
        "━━━━━━━━━━━━━━\n"
        "🏦 *Kuda Bank*\n"
        "👤 Olaotan Olamide\n"
        "🔢 `2082773155`\n"
        "━━━━━━━━━━━━━━\n\n"
        "After payment, type /paid 💰",
        parse_mode="Markdown"
    )

async def paid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "✅ Payment noted.\n\n"
        "Admin will confirm your subscription shortly 💼"
    )
    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 User {user_id} requested subscription confirmation."
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    add_or_get_user(user_id, username)
    increment_messages(user_id)

    # Check expiry
    if check_expiry(user_id):
        msg = get_unique_message(user_id, PREMIUM_MESSAGES)
        await update.message.reply_text(msg)
        return

    # Determine step
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT messages_sent FROM users WHERE user_id=?", (user_id,))
    step = c.fetchone()[0]
    conn.close()

    if step <= FREE_LIMIT:
        msg = get_unique_message(user_id, FREE_MESSAGES)
    else:
        msg = get_unique_message(user_id, GATED_MESSAGES) + "\n\nType /help when ready to unlock full guidance 💼"
    await update.message.reply_text(msg)

# ======================
# ADMIN COMMANDS
# ======================
async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    total_users = len(get_all_users())
    paid_users = len(get_paid_users())
    revenue = get_revenue()

    await update.message.reply_text(
        f"🔥 Ola Admin Dashboard 🔥\n\n"
        f"Total Users: {total_users}\n"
        f"Paid Users: {paid_users}\n"
        f"Revenue: ₦{revenue}\n\n"
        "Commands:\n"
        "✅ /confirm <user_id> <plan>\n"
        "❌ /revoke <user_id>\n"
        "📊 /stats\n"
        "📢 /broadcast <message>"
    )

async def confirm_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return

    try:
        args = context.args
        target_id = int(args[0])
        plan = args[1].lower()
        plan_days = {"2d":2, "1w":7, "1m":30, "life":365*50}  # life = 50 years
        amount_dict = {"2d":2000, "1w":6000, "1m":25000, "life":100000}
        set_paid(target_id, plan, plan_days[plan], amount_dict[plan])
        await update.message.reply_text(f"✅ User {target_id} confirmed for {plan} plan.")
        await context.bot.send_message(chat_id=target_id, text="💎 Your subscription has been activated! Enjoy premium guidance 💼🔥")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def revoke_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    try:
        target_id = int(context.args[0])
        revoke_paid(target_id)
        await update.message.reply_text(f"❌ User {target_id} subscription revoked.")
        await context.bot.send_message(chat_id=target_id, text="❌ Your subscription has been revoked by admin.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    total_users = len(get_all_users())
    paid_users = len(get_paid_users())
    revenue = get_revenue()
    await update.message.reply_text(
        f"📊 Stats:\nTotal Users: {total_users}\nPaid Users: {paid_users}\nRevenue: ₦{revenue}"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Not authorized.")
        return
    try:
        msg = " ".join(context.args)
        users = get_all_users()
        count = 0
        for u in users:
            try:
                await context.bot.send_message(chat_id=u[0], text=msg)
                count += 1
            except:
                continue
        await update.message.reply_text(f"📢 Broadcast sent to {count} users.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ======================
# MAIN
# ======================
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # User commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("paid", paid_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Admin commands
    app.add_handler(CommandHandler("admin", admin_dashboard))
    app.add_handler(CommandHandler("confirm", confirm_user))
    app.add_handler(CommandHandler("revoke", revoke_user))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast, filters=filters.TEXT))

    app.run_polling()

if __name__ == "__main__":
    main()
