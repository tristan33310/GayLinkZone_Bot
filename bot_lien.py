import os
import re
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler,
    CommandHandler, filters
)

TOKEN = os.environ["TELEGRAM_TOKEN"]
GROUP_ID = int(os.environ["GROUP_ID"])      
OWNER_ID = int(os.environ["OWNER_ID"])       

banned_terms = [
    "cp", "c.p", "c_p", "ped0", "pedo", "13yo", "14yo", "underage", "under4ge",
    "lo.li", "loli", "preteen", "zoophile", "zoophilie", "mineur", "mineure",
    "13 y/o", "p3d0", "péd0", "viol", "inceste", "twincest", "childlove", "boylove",
    "babylover", "jailbait", "gamin", "gamine", "childporn", "enfantnu", "nudekid"
]

INFO_MESSAGE = (
    "🔞 Gay Telegram links only. Adults 18+.\n"
    "🚫 Forbidden content (will be reported and banned):\n"
    "- CP / child-related content\n"
    "- Zoophilia / bestiality\n"
    "- Non-consensual material\n"
    "- Any underage or illegal content\n"
    "✅ To share a Telegram link, message the bot: @RainbowLinkHub_bot"
)

flask_app = Flask(__name__)
@flask_app.route('/')
def index():
    return "Bot actif !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

def has_banned_content(text):
    return any(term.replace(".", "") in normalize(text) for term in banned_terms)

def contains_telegram_link(text):
    return re.search(r"(https?://)?t\\.me/\\w+", text)

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

    msg = update.message.text
    user = update.effective_user
    username = user.username or user.first_name or str(user.id)

    print(f"[REÇU] De: {username} | Message: {msg}")

    # Envoi au propriétaire
    await context.bot.send_message(chat_id=OWNER_ID, text=f"📥 {username} → {msg}")

    if has_banned_content(msg):
        print(f"[BLOQUÉ] Mot interdit détecté dans le message de {username}")
        return

    if contains_telegram_link(msg):
        print(f"[PUBLIÉ] Lien Telegram validé par {username}")
        await context.bot.send_message(chat_id=GROUP_ID, text=msg)
        await context.bot.send_message(chat_id=GROUP_ID, text=INFO_MESSAGE)
    else:
        print(f"[IGNORÉ] Aucun lien valide dans le message de {username}")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=GROUP_ID, text=INFO_MESSAGE)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, handle_message))

    app.job_queue.run_repeating(send_reminder, interval=10800, first=10)

    threading.Thread(target=run_flask).start()
    print("Bot running...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
