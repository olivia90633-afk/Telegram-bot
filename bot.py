import os
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# ======================
# ENV VARIABLES
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ======================
# USER STATE
# ======================
user_steps = {}      # message count
user_history = {}    # prevent repetition

MAX_FREE_MESSAGES = 5

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_steps[user_id] = 0
    user_history[user_id] = []

    await update.message.reply_text(
        "🔥 *Ola AI*\n\n"
        "Do you want to start making serious money and escape poverty?\n\n"
        "Reply *YES* 💼💰",
        parse_mode="Markdown"
    )

# ======================
# MAIN CHAT
# ======================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    step = user_steps.get(user_id, 0)
    user_steps[user_id] = step + 1

    # 🔒 FORCE SUBSCRIPTION AFTER LIMIT
    if step >= MAX_FREE_MESSAGES:
        await update.message.reply_text(
            "💎 You’re clearly serious about money.\n\n"
            "The next level is reserved for disciplined minds.\n\n"
            "Type /help to unlock the real blueprint 💰🚀"
        )
        return

    # ======================
    # OPENAI PROMPT
    # ======================
    prompt = f"""
You are Ola AI — a serious, elite wealth mentor.

Rules:
- Talk ONLY about money, wealth, business, success, freedom.
- Be professional, confident, teasing, motivating.
- NEVER repeat previous ideas.
- Use examples like N500k → N5M → N50M → $1M+.
- Encourage curiosity.
- Sound realistic, not scammy.
- Emojis allowed but classy.
- Reply intelligently to what user said.

User message:
"{text}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a billionaire money mentor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )

        reply = response.choices[0].message.content.strip()

        # prevent accidental repetition
        if reply in user_history[user_id]:
            reply += "\n\nSmart money always looks for the next level 📈💼"

        user_history[user_id].append(reply)

    except Exception:
        # 🔥 FAILSAFE (BOT NEVER GOES SILENT)
        reply = random.choice([
            "Money rewards those who act early 💼📈",
            "The wealthy think differently — I can show you 🧠💰",
            "There is a system behind every millionaire 💎",
            "Cashflow beats salary every single time 🔥",
            "Serious money requires serious mindset 🚀",
        ])

    await update.message.reply_text(reply)

# ======================
# HELP / SUBSCRIBE
# ======================
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

# ======================
# MAIN
# ======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
