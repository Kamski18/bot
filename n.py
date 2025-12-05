import telebot

BOT_TOKEN = "8376202221:AAEeDGSrvUKgGmpJX8F5N7s5sNRjd4vpvlY"
ADMIN_CHAT_ID = (1160508602, 1981928681)

bot = telebot.TeleBot(BOT_TOKEN)

# Track /auth state
user_waiting = {}


# -------------------------
# MarkdownV2 Escape Function
# -------------------------
def escape_md(text: str) -> str:
    """
    Escape Telegram MarkdownV2 special characters.
    """
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in escape_chars:
        text = text.replace(ch, "\\" + ch)
    return text


# -------------------------
# /start
# -------------------------
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.reply_to(message, "Hello! Use /auth to send your authentication string.")


# -------------------------
# /auth
# -------------------------
@bot.message_handler(commands=['auth'])
def auth_cmd(message):
    chat_id = message.chat.id
    user_waiting[chat_id] = True
    bot.reply_to(message, "Please enter your name, form, class and your email:")


# -------------------------
# /send — ADMIN ONLY
# -------------------------
@bot.message_handler(commands=['send'])
def admin_send(message):
    if message.from_user.id not in ADMIN_CHAT_ID:
        return

    try:
        parts = message.text.split(" ", 2)
        user_id = int(parts[1])
        text_to_send = parts[2]
    except:
        bot.reply_to(
            message,
            "Usage:\n`/send <user_id> <message>`",
            parse_mode="Markdown"
        )
        return

    try:
        bot.send_message(user_id, text_to_send)
        bot.reply_to(
            message,
            f"✅ Message sent to `{user_id}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to send: {e}")


# -------------------------
# Catch-All Handler
# -------------------------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if user_waiting.get(chat_id):

        # Escape everything sent by the user
        auth_string = escape_md(message.text)

        first = escape_md(message.from_user.first_name or "")
        username = escape_md(message.from_user.username or "")
        user_id = escape_md(str(message.from_user.id))

        # Notify admins
        for admin in ADMIN_CHAT_ID:
            bot.send_message(
                admin,
                f"🔐 *New Authentication Attempt*\n"
                f"👤 User: {first} `({user_id})` \\(@{username}\\)\n"
                f"📝 String: `{auth_string}`",
                parse_mode="MarkdownV2"
            )

        bot.reply_to(message, "Thanks! Your code has been recorded.")
        user_waiting[chat_id] = False

    else:
        bot.reply_to(message, "Unknown command. Use /auth to submit your string.")


# -------------------------
# Start bot
# -------------------------
bot.polling()
