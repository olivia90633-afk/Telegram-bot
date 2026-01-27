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

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ======================
# USER STATE
# ======================
user_steps = {}        # message count
user_used_msgs = {}    # track used messages
paid_users = set()     # temporary (we’ll persist later)

FREE_LIMIT = 5

# ======================
# PRE-SAVED MONEY MESSAGES (FREE)
# ======================
FREE_MESSAGES = [
    "Money doesn’t respond to wishes — it responds to strategy 💼📊",
    "Most people work hard, few people work smart. Wealth lives in the difference 💡💰",
    "Salary keeps you busy, systems make you wealthy 📈",
    "The rich don’t chase money, they build value 💎",
    "There’s a reason some people escape poverty — they learn different rules 🧠",
    "Real money is predictable when you understand leverage 🚀",
    "You don’t need luck to be rich, you need structure 🏗️",
    "Poverty is expensive. Wealth requires discipline 💼",
    "People who win financially think long-term, not urgent ⏳",
    "Money grows faster when emotions are removed 📊",
]

# ======================
# PRE-SAVED GATED MESSAGES (AFTER FREE)
# ======================
GATED_MESSAGES = [
    "I can guide you properly, but I won’t mislead you with half-information 💼",
    "Serious income systems require commitment — not curiosity alone 🔐",
    "At this stage, guidance must be structured, not random 📈",
    "This is where most people stop — disciplined ones continue 🚪",
    "Once access is unlocked, I’ll break things down step by step 💎",
    "I don’t sell dreams — I teach systems, and systems are premium 🧠",
    "Wealth blueprints are protected for a reason 🔒",
    "You’re asking the right questions — now commitment matters 💼",
]

# ======================
# PREMIUM MESSAGES (AFTER /paid)
# ======================
PREMIUM_MESSAGES = [
    "Welcome. Now we talk seriously about money and execution 💼🔥",
    "First rule of wealth: control income before increasing lifestyle 📊",
    "Money respects structure. Let’s build yours properly 🏗️",
    "From here, we focus on skills, leverage, and systems 📈",
    "This is where transformation actually starts 🚀",
]

# ======================
# START
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_steps[user_id] = 0
    user_used_msgs[user_id] = set()

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
    user_text = update.message.text.lower().strip()

    # PAID USER FLOW
    if user_id in paid_users:
        msg = get_unique_message(user_id, PREMIUM_MESSAGES)
        await update.message.reply_text(msg)
        return

    # FREE / GATED FLOW
    step = user_steps.get(user_id, 0)
    user_steps[user_id] = step + 1

    if step < FREE_LIMIT:
        msg = get_unique_message(user_id, FREE_MESSAGES)
    else:
        msg = get_unique_message(user_id, GATED_MESSAGES) + \
              "\n\nType /help when you’re ready to unlock full guidance 💼"

    await update.message.reply_text(msg)

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
        "After payment, type /paid 💰",
        parse_mode="Markdown"
    )

# ======================
# PAID (TEMP CONFIRM)
# ======================
async def paid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    paid_users.add(user_id)

    await update.message.reply_text(
        "✅ Payment noted.\n\n"
        "Welcome to the serious money side 💼🔥\n"
        "Let’s begin."
    )

# ======================
# HELPERS
# ======================
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
# MAIN
# ======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("paid", paid_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
