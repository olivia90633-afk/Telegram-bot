import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

user_steps = {}  # track message count per user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_steps[user_id] = 0

    await update.message.reply_text(
        "🔥 Ola AI\n\nDo you want to start making serious money and escape poverty?\nReply YES 💼💰"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    step = user_steps.get(user_id, 0)
    user_steps[user_id] = step + 1

    # After 5 messages → force subscription
    if step >= 5:
        await update.message.reply_text(
            "💎 The real wealth blueprint is reserved for serious people.\n\n"
            "Type /help to unlock powerful money secrets 💰🚀"
        )
        return

    prompt = f"""
You are a serious, professional money mentor AI.
User said: "{text}"

Reply intelligently, motivational, business-minded.
Tease wealth, success, millions, freedom.
Encourage user subtly.
Use emojis but stay professional.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    await update.message.reply_text(response.choices[0].message.content)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💎 SUBSCRIPTION PLANS 💎\n\n"
        "🔥 ₦2,000 → 2 Days\n"
        "💎 ₦6,000 → 1 Week\n"
        "💰 ₦25,000 → 1 Month\n"
        "👑 ₦100,000 → Lifetime\n\n"
        "🏦 Kuda Bank\n"
        "👤 Olaotan Olamide\n"
        "🔢 2082773155\n\n"
        "After payment, type /paid 💰"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
