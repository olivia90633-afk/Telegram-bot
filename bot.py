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

# Track how many messages each user sent
user_steps = {}

FREE_LIMIT = 5  # after this, we gate deep secrets

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_steps[user_id] = 0

    await update.message.reply_text(
        "🔥 *Ola AI*\n\n"
        "Do you want to start making serious money and escape poverty?\n\n"
        "Reply *YES* 💼💰",
        parse_mode="Markdown"
    )

# ======================
# CHAT
# ======================
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()

    step = user_steps.get(user_id, 0)
    user_steps[user_id] = step + 1

    # Decide mode
    if step < FREE_LIMIT:
        mode = "free"
    else:
        mode = "gated"

    # ======================
    # PROMPT
    # ======================
    if mode == "free":
        prompt = f"""
You are Ola AI, a professional wealth mentor.

Reply intelligently to the user.
Focus on:
- Money mindset
- Business thinking
- Wealth growth
- Financial freedom
- Realistic encouragement

Do NOT repeat ideas.
Do NOT ask for payment yet.
Be serious, motivating, persuasive.
Use classy emojis.

User said:
"{user_text}"
"""
    else:
        prompt = f"""
You are Ola AI, a professional wealth mentor.

Reply intelligently to the user.
You may still talk about money, success, mindset.

BUT:
- Do NOT reveal deep strategies or step-by-step systems
- Hint that full guidance requires commitment
- Encourage subscription in DIFFERENT intelligent ways
- Do NOT repeat phrases
- Sound exclusive, premium, disciplined

Examples of tone:
- "I can guide you properly once access is unlocked"
- "Serious strategies are reserved for committed minds"
- "I don’t want to mislead you with half-information"

User said:
"{user_text}"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a serious billionaire mentor AI."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
        )

        reply = response.choices[0].message.content.strip()

    except Exception:
        reply = (
            "Real wealth is built with clarity, patience, and the right guidance 💼📈"
        )

    await update.message.reply_text(reply)

# ======================
# HELP
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
        "Once unlocked, I’ll guide you properly 💼🚀",
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
