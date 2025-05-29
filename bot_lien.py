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
    "cp", "c.p", "c_p", "ped0", "pedo", "p3d0", "péd0",
    "13yo", "14yo", "underage", "under4ge", "preteen", "pre-teen",
    "lolita", "loli", "lo.li", "lolicon",
    "childlove", "boylove", "babylover", "jailbait",
    "childporn", "childnude", "nudekid", "youngnude", "enfantnu",
    "mineur", "mineure", "gamin", "gamine",
    "incest", "inceste", "twincest",
    "dadson", "dadandson", "daddyson", "fatherandson", "father+son",
    "stepdad", "stepfather", "stepbrother", "stepson",
    "nonconsensual", "rape", "viol"
]

def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())

def has_banned_content(text):
    return any(term.replace(".", "") in normalize(text) for term in banned_terms)

def contains_telegram_link(text):
    return re.search(r"(https?://)?t\.me/[\w\d@+\-_/=]+", text)

# --- UTILISATEURS BLOQUÉS ---
banned_users = [
    # Ajouter ici les user_id à bloquer
]

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

# --- MESSAGE D’ACCUEIL ---
WELCOME_MESSAGE = (
    "\n"
    "👋 <b>Welcome!</b>\n"
    "<b>This bot is intended solely for sharing Gay Telegram links with adult content (18+).</b>\n"
    "\n"
    "🤖 This bot does not reply to messages. It is only designed to receive valid Telegram links.\n"
    "\n"
    "🚫 No external links (social media, websites, file hosts, etc.), paid links, or story links will be accepted.\n"
    "\n"
    "🚫 <b>Strictly prohibited content:</b>\n"
    "- Any material involving minors (CP or any child-related content, real or fictional)\n"
    "- Zoophilia or bestiality\n"
    "- Non-consensual content (rape, voyeurism, revenge porn, etc.)\n"
    "- Extreme violence or mutilation\n"
    "- Gore or macabre content\n"
    "- Threats, harassment, or doxxing\n"
    "- Identity theft or impersonation\n"
    "- Terrorist or extremist propaganda\n"
    "- Sale of drugs or weapons\n"
    "- Scams or fraudulent content\n"
    "- Any content that violates laws or Telegram’s Terms of Service\n"
    "\n"
    "🚫 <b>Any violation of these rules will result in an immediate and permanent ban.</b>\n"
    "\n"
    "⚠️ <b>Note:</b> Random Telegram invite links /+abc<b>CP</b>xyz may accidentally contain letter combinations like 'CP' that match our content filters.If your link is rejected for this reason, please regenerate a new one.\n"
    "\n"
    "✅ To submit a link, simply paste a valid Telegram link here.\n"
    "If accepted, it will be published to the group."
    "\n"
)

# --- HANDLERS ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    msg = update.message.text.strip()
    user = update.effective_user
    username = user.username or user.first_name or str(user.id)

    # ⛔ Ignore banned users
    if user.id in banned_users:
        await context.bot.send_message(chat_id=OWNER_ID, text=f"🚫 Ignored message from banned user {username} ({user.id})")
        return

    # 🔁 Forward to OWNER_ID
    try:
        await context.bot.forward_message(
            chat_id=OWNER_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        logging.warning(f"Erreur lors du forward au OWNER_ID : {e}")

    # 🔍 Filtrage
    if has_banned_content(msg):
        await update.message.reply_text(
            "🚫 This link contains prohibited terms and will not be published.",
            parse_mode="HTML"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=f"❌ Message from {username} was blocked.")
        return

    if contains_telegram_link(msg):
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"‎\n‎\n🔗 {msg.strip()} \n‎\n‎",
            disable_web_page_preview=True
        )
        await update.message.reply_text(
            "✅ Your link has been published successfully.",
            parse_mode="HTML"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=f"✅ Message from {username} was published.")

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
        text=(
            "\n"
            "🔞 <b>Gay Telegram links only. Adults 18+.</b>\n\n"
            "This is a participative project — feel free to share your best Telegram group or channel link!\n\n"
            "🚫 <b>No paid, financially motivated, or story links</b>\n\n"
            "🚫 <b>Strictly prohibited content:</b>\n"
            "\n"
            "- Any material involving minors (CP real or fictional)\n"
            "- Zoophilia or bestiality\n"
            "- Non-consensual content (rape, voyeurism, revenge porn, etc.)\n"
            "- Extreme violence or mutilation\n"
            "- Gore or macabre content\n"
            "- Threats, harassment, or doxxing\n"
            "- Identity theft or impersonation\n"
            "- Terrorist or extremist propaganda\n"
            "- Sale of drugs or weapons\n"
            "- Scams or fraudulent content\n"
            "- Any content that violates laws or Telegram’s Terms of Service\n\n"
            "🚫 <b>Any violation of these rules will result in an immediate and permanent ban.</b>\n\n"
            "✅ To share a Telegram link, message the bot: @RainbowLinkHub_bot""\n"
        ),
        disable_web_page_preview=True,
        parse_mode="HTML"
    )
    save_message_id(message.message_id)

# --- MAIN ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # HANDLERS
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_message))

    # JOB SCHEDULER
    job_queue: JobQueue = app.job_queue
    job_queue.run_repeating(auto_post, interval=3 * 60 * 60, first=5)

    # WEBHOOK (Render)
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
