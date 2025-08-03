# MikroTechAcademy Bot - Final Version (Corrected for Deployment)
# File: bot.py

import logging
import os
import sys
import asyncio
from math import ceil

from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Load variables from .env file when running locally
load_dotenv()

# --- Basic Setup ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CLIENT_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# --- Conversation States ---
SELECTING_COUNTRY, SELECTING_SERVICE, SELECTING_TUTOR_OPTION, AWAITING_ASSIGNMENT, AWAITING_NAME, AWAITING_PHONE, AWAITING_SUBJECT = range(
    7)

# --- Data & Pricing ---
RATES = {
    'USD': 1.25, 'CAD': 1.70, 'AED': 4.60, 'SAR': 4.70,
    'QAR': 4.55, 'KWD': 0.38, 'GBP': 1.00,
}
COUNTRIES = {
    'uk': {'name': 'UK', 'currency': 'GBP'}, 'kw': {'name': 'Kuwait', 'currency': 'KWD'},
    'ae': {'name': 'United Arab Emirates', 'currency': 'AED'}, 'sa': {'name': 'Saudi Arabia', 'currency': 'SAR'},
    'qa': {'name': 'Qatar', 'currency': 'QAR'}, 'us': {'name': 'USA', 'currency': 'USD'},
    'ca': {'name': 'Canada', 'currency': 'CAD'},
}


# --- Helper Functions ---
def get_rounded_price(base_price_gbp: int, target_currency: str) -> int | None:
    rate = RATES.get(target_currency)
    if not rate:
        logger.error(f"No rate found for currency: {target_currency}")
        return None
    converted = base_price_gbp * rate
    return int(5 * ceil(converted / 5)) if converted >= 20 else int(ceil(converted))


# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the conversation.")
    keyboard = [
        [InlineKeyboardButton("🇬🇧 UK", callback_data='country_uk'),
         InlineKeyboardButton("🇰🇼 Kuwait", callback_data='country_kw')],
        [InlineKeyboardButton("🇦🇪 UAE", callback_data='country_ae'),
         InlineKeyboardButton("🇸🇦 Saudi Arabia", callback_data='country_sa')],
        [InlineKeyboardButton("🇶🇦 Qatar", callback_data='country_qa'),
         InlineKeyboardButton("🇺🇸 USA", callback_data='country_us')],
        [InlineKeyboardButton("🇨🇦 Canada", callback_data='country_ca')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Welcome to MikroTechAcademy! 🤖\n\nPlease select the country where you are studying:"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)
    return SELECTING_COUNTRY


async def show_services_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_country_name = context.user_data['country']['name']
    keyboard = [
        [InlineKeyboardButton("📝 Assignment / Project Help", callback_data='service_assignment')],
        [InlineKeyboardButton("🧑‍🏫 Private Lessons", callback_data='service_lesson')],
        [InlineKeyboardButton("💬 Connect with a Tutor", callback_data='service_tutor')],
        [InlineKeyboardButton("💷 Prices and Info", callback_data='service_info')],
        [InlineKeyboardButton("⬅️ Change Country", callback_data='go_back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"You've selected *{user_country_name}*.\n\nHow can I help you today?"
    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
    return SELECTING_SERVICE


async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    country_code = query.data.split('_')[1]
    context.user_data['country'] = COUNTRIES[country_code]
    logger.info(f"User {query.from_user.id} selected country: {country_code.upper()}")
    return await show_services_menu(update, context)


async def request_assignment_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Please upload a file, an image, or type a description of the assignment.\n\nTo go back, press /cancel.")
    return AWAITING_ASSIGNMENT


async def handle_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_country = context.user_data.get('country', {'name': 'Unknown'})['name']
    logger.info(f"Received assignment from user {user.id}")
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID,
                                   text=f"🔔 *New Assignment*\n\n*From:* {user.first_name} (`{user.id}`)\n*Country:* {user_country}",
                                   parse_mode='Markdown')
    await context.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=update.message.chat_id,
                                      message_id=update.message.message_id)
    await update.message.reply_text("✅ Thank you! Your assignment has been sent. A tutor will contact you shortly.")
    return ConversationHandler.END


async def show_tutor_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📄 Fill Info Form", callback_data='tutor_fill_form')],
        [InlineKeyboardButton("📲 Connect via Telegram", callback_data='tutor_direct_connect')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="How would you like to connect with a tutor?", reply_markup=reply_markup)
    return SELECTING_TUTOR_OPTION


async def tutor_direct_connect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_country = context.user_data.get('country', {'name': 'Unknown'})['name']
    user_chat_link = f"tg://user?id={user.id}"
    logger.info(f"User {user.id} requested direct connection.")
    admin_text = (
        f"🔔 *Direct Connection Request*\n\n"
        f"User *{user.first_name}* from *{user_country}* wants to connect directly.\n\n"
        f"➡️ [Click here to chat with {user.first_name}]({user_chat_link})"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode='Markdown')
    await query.edit_message_text(
        "✅ The admin has been notified!\nA tutor will contact you directly on Telegram shortly.")
    return ConversationHandler.END


async def request_details_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['service_choice'] = query.data
    await query.edit_message_text(text="Of course. Let's get a few details.\n\nFirst, what is your full name?")
    return AWAITING_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Thanks! What is your phone number? (Include country code)")
    return AWAITING_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Perfect. And what subject do you need help with?")
    return AWAITING_SUBJECT


async def finalise_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['subject'] = update.message.text
    user = update.message.from_user
    user_data = context.user_data
    user_country = user_data.get('country', {'name': 'Unknown'})['name']
    service = user_data.get('service_choice', 'service_lesson')
    title = "Private Lesson Request" if service == 'service_lesson' else "Tutor Request (Form)"
    logger.info(f"Finalizing '{title}' for user {user.id}")
    admin_message = (
        f"🔔 *New {title}!*\n\n"
        f"*Name:* {user_data.get('name', 'N/A')}\n"
        f"*Phone:* {user_data.get('phone', 'N/A')}\n"
        f"*Subject:* {user_data.get('subject', 'N/A')}\n"
        f"*Country:* {user_country}\n"
        f"*User ID:* `{user.id}`"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode='Markdown')
    await update.message.reply_text("✅ All set! We've sent your request. A tutor will be in touch shortly.",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def show_price_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    country_info = context.user_data['country']
    currency_code = country_info['currency']
    price1, price2, price3 = get_rounded_price(40, currency_code), get_rounded_price(35,
                                                                                     currency_code), get_rounded_price(
        30, currency_code)
    if price1 is None:
        await query.edit_message_text("Sorry, pricing information for your region is currently unavailable.")
        return SELECTING_SERVICE
    price_text = (
        f"💰 *Pricing & Info ({country_info['name']})*\n\n"
        f"🔹 *Individual:* `{price1} {currency_code}`\n"
        f"🔹 *Group (2-3):* `{price2} {currency_code}` /student\n"
        f"🔹 *Group (4+):* `{price3} {currency_code}` /student\n\n"
        f"ℹ️ *Info*\n— Lessons are online via Zoom.\n— UK flexible payment options.\n— Completion certificates available."
    )
    keyboard = [[InlineKeyboardButton("⬅️ Back to Services", callback_data='back_to_services')]]
    await query.edit_message_text(text=price_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SELECTING_TUTOR_OPTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} cancelled the conversation.")
    await update.message.reply_text("Operation cancelled. Type /start to begin again.",
                                    reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


# --- Application Setup ---
if not BOT_TOKEN:
    logger.fatal("FATAL: TELEGRAM_BOT_TOKEN environment variable not set!")
    sys.exit(1)

ptb_app = Application.builder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECTING_COUNTRY: [CallbackQueryHandler(select_country, pattern='^country_')],
        SELECTING_SERVICE: [
            CallbackQueryHandler(request_assignment_upload, pattern='^service_assignment$'),
            CallbackQueryHandler(request_details_start, pattern='^service_lesson$'),
            CallbackQueryHandler(show_tutor_options, pattern='^service_tutor$'),
            CallbackQueryHandler(show_price_info, pattern='^service_info$'),
            CallbackQueryHandler(start, pattern='^go_back_to_start$'),
        ],
        SELECTING_TUTOR_OPTION: [
            CallbackQueryHandler(request_details_start, pattern='^tutor_fill_form$'),
            CallbackQueryHandler(tutor_direct_connect, pattern='^tutor_direct_connect$'),
            CallbackQueryHandler(show_services_menu, pattern='^back_to_services$'),
        ],
        AWAITING_ASSIGNMENT: [MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_assignment)],
        AWAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        AWAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        AWAITING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalise_request)],
    },
    fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
)
ptb_app.add_handler(conv_handler)

# --- Webhook Setup (for Deployment) ---
app = Flask(__name__)


# The `startup` function will be called by the build command on Render.
async def startup():
    """Initialize the bot application and set the webhook."""
    logger.info("Initializing application and setting webhook...")
    await ptb_app.initialize()
    if WEBHOOK_URL:
        await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}", allowed_updates=Update.ALL_TYPES)
        logger.info(f"Webhook set to {WEBHOOK_URL}/{BOT_TOKEN}")
    else:
        logger.info("WEBHOOK_URL not set, skipping webhook setup.")


@app.route("/")
def index():
    return "Bot is running!"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    """This function receives and processes updates directly."""
    logger.info("--- Webhook received an update ---")
    try:
        # The application is already initialized by the startup process.
        # We can directly process the update.
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, ptb_app.bot)
        await ptb_app.process_update(update)
        logger.info("--- Update processed successfully ---")
    except Exception as e:
        logger.error(f"Error processing update: {e}")

    return "OK"


# --- Main Execution Block ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'setup_webhook':
        # This is called by Render's build command
        logger.info("Running startup and webhook setup...")
        asyncio.run(startup())
    else:
        # This block is for local testing only
        print("Bot is running locally in polling mode...")
        # The run_polling() method handles initialization automatically.
        ptb_app.run_polling()
