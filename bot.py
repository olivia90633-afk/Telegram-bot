import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from database import add_user, get_user, increment_messages, set_premium, stats
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ADMIN_ID = 7926402001
ADMIN_PASSWORD = "765432"

client = OpenAI(api_key=OPENAI_API_KEY)

INTRO_MESSAGES = [
    "Wealth is a skill, not luck 💼",
    "Money flows to disciplined minds 💰",
    "Trading is patience + strategy 📊",
    "Rich people think long-term 🧠",
    "Consistency beats motivation 🔥",
    "Smart income beats hard labor 🚀",
    "Charts tell stories most ignore 📉📈",
    "Risk management creates wealth 💎",
    "Traders survive before they profit 🛡️",
    "Small wins compound into millions 💵"
]

SUB_MESSAGE = (
    "🔥 You’ve reached the gateway.\n\n"
    "Serious traders invest in knowledge.\n"
    "Use /help to unlock full IQ Option trading mastery 💰📊"
)

HELP_TEXT = """
💎 PREMIUM ACCESS 💎

📈 IQ Option Trading Blueprint
🧠 Full beginner → pro strategy
💰 Risk management
📊 Market psychology

🏦 Kuda Bank
👤 Olaotan Olamide
🔢 2082773155

After payment, type:
/paid YOUR_TRANSACTION_NOTE
"""

PREMIUM_CONTENT = """
📊 IQ OPTION WEALTH SYSTEM

1️⃣ Choose 1–5 min timeframe
2️⃣ Trade ONLY trend direction
3️⃣ Use support & resistance
4️⃣ Risk max 2% per trade
5️⃣ Avoid overtrading
6️⃣ Journal every trade
7️⃣ Compound slowly

This is how real traders win 🧠💰
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(
        "🔥 Ola AI\n\nDo you want to start making serious money and escape poverty?\n\nReply YES 💼💰"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_premium(update.effective_user.id, 1)
    await update.message.reply_text(
        "✅ Payment received.\n\nWelcome to the inner circle 💎💰"
    )
    await update.message.reply_text(PREMIUM_CONTENT)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total, premium = stats()
    await update.message.reply_text(
        f"👑 ADMIN PANEL\n\n"
        f"👥 Users: {total}\n"
        f"💎 Premium: {premium}\n\n"
        f"/broadcast MESSAGE\n"
        f"/confirm USER_ID\n"
        f"/cancel USER_ID"
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast message")
        return

    msg = " ".join(context.args)
    from database import cursor
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for uid in users:
        try:
            await context.bot.send_message(uid[0], msg)
        except:
            pass


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    add_user(user_id, update.effective_user.username)
    increment_messages(user_id)

    user = get_user(user_id)
    messages = user[2]
    premium = user[3]

    if premium:
        await update.message.reply_text(PREMIUM_CONTENT)
        return

    if messages >= 5:
        await update.message.reply_text(SUB_MESSAGE)
        return

    prompt = f"User says: {text}. Respond as a smart trading mentor."

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    await update.message.reply_text(res.choices[0].message.content)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("paid", paid))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # ✅ THIS LINE FIXES YOUR ERROR
    app.run_polling()


if __name__ == "__main__":
    main()
