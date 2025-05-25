import os
import re
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ["TELEGRAM_TOKEN"]  # Token sécurisé depuis Render uniquement

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if has_banned_content(msg):
        try:
            await update.message.delete()
            await update.message.reply_text("⛔️ Message bloqué.")
        except:
            pass
    elif contains_telegram_link(msg):
        await update.message.reply_text("✅ Lien accepté.")
    else:
        try:
            await update.message.delete()
        except:
            pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    flask_app = Flask(__name__)
    @flask_app.route('/')
    def index():
        return "Bot actif !"

    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host="0.0.0.0", port=port)

    threading.Thread(target=run_flask).start()
    app.run_polling()
