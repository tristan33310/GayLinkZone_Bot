import os
import re
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    JobQueue,
)

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
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

# --- STOCKAGE ID MESSAGE AUTO ---
ID_FILE = "last_post_id.txt"

def save_message_id(msg_id):
    with open(ID_FILE, "w") as f:
        f.write(str(msg_id))

def load_message_id():
    try:
        with open(ID_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return None

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
        "✅ To submit a link, just paste a valid Telegram link here\n"
        "It will be published to the group if accepted."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    msg = update.message.text.strip()
    user = update.effective_user
    username = user.username or user.first_name or str(user.id)

    # Message au propriétaire
    await context.bot.send_message(chat_id=OWNER_ID, text=f"📥 {username} → {msg}")

    if has_banned_content(msg):
        await update.message.reply_text("🚫 This link contains prohibited terms and will not be published.")
        return

    if contains_telegram_link(msg):
        await context.bot.send_message(chat_id=GROUP_ID, text=f"‎\n‎\n🔗 {msg.strip()} \n‎\n‎")
        await update.message.reply_text("✅ Your link has been published successfully.")

# --- MESSAGE RÉCURRENT ---
async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    old_id = load_message_id()
    try:
        if old_id:
            await context.bot.delete_message(chat_id=GROUP_ID, message_id=old_id)
    except Exception as e:
        logging.warning(f"Erreur suppression message: {e}")

    message = await context.bot.send_message(
        chat_id=GROUP_ID,
        text="🔞 Gay Telegram links only. Adults 18+.\n\n✅ To share a Telegram link, message the bot: @RainbowLinkHub_bot"
    )
    save_message_id(message.message_id)

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLERS
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))

    # JOB SCHEDULER
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(auto_post, interval=3 * 60 * 60, first=5)

    # WEBHOOK (Render)
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{WEBHOOK_URL}",
    )
