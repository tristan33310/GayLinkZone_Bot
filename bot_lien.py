import os
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# --- ENV ---
TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])
OWNER_ID = int(os.environ["OWNER_ID"])
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# --- FILTRAGE ---
banned_terms = [
    "cp", "c.p", "c_p", "ped0", "pedo", "13yo", "14yo", "underage", "under4ge",
    "lo.li", "loli", "preteen", "zoophile", "zoophilie", "mineur", "mineure",
    "13 y/o", "p3d0", "péd0", "viol", "inceste", "twincest", "childlove", "boylove",
    "babylover", "jailbait", "gamin", "gamine", "childporn", "enfantnu", "nudekid"
]

def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

def has_banned_content(text):
    return any(term.replace(".", "") in normalize(text) for term in banned_terms)

def contains_telegram_link(text):
    return re.search(r"(https?://)?t\.me/\w+", text)

# --- HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n"
        "🔞 This bot only accepts Telegram links for adult content (18+).\n"
        "🚫 Forbidden content:\n"
        "- CP / child-related content\n"
        "- Zoophilia\n"
        "- Non-consensual material\n"
        "- Any underage or illegal content\n"
        "✅ To submit a link, just paste a valid Telegram link here (e.g. https://t.me/example)\n"
        "It will be published to the group if accepted."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    msg = update.message.text.strip()
    user = update.effective_user
    username = user.username or user.first_name or str(user.id)

    await context.bot.send_message(chat_id=OWNER_ID, text=f"📥 {username} → {msg}")

    if has_banned_content(msg):
        return

    if contains_telegram_link(msg):
        await context.bot.send_message(chat_id=GROUP_ID, text=f"\n🔗 {msg}\n")

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))

    # Démarrage avec webhook (Render)
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
        url_path=TOKEN
    )
