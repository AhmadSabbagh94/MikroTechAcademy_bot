# MikroTechAcademy Bot - Final Stable Version
# File: bot.py

import logging
import os
from math import ceil
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
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
# --- Basic Setup ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration (Loaded from Environment Variables) ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CLIENT_ID")

# --- Conversation States ---
SELECTING_COUNTRY, SELECTING_SERVICE, SELECTING_TUTOR_OPTION, AWAITING_ASSIGNMENT, AWAITING_NAME, AWAITING_PHONE, AWAITING_SUBJECT = range(
    7)

# --- Data & Pricing ---
# Using a fixed dictionary for rates is more reliable than a live service.
# You can update these rates manually whenever you want.
RATES = {
    'USD': 1.35,  # 1 GBP = 1.25 USD
    'CAD': 1.85,  # 1 GBP = 1.70 CAD
    'AED': 4.96,  # 1 GBP = 4.60 AED
    'SAR': 5.00,  # 1 GBP = 4.70 SAR
    'QAR': 4.91,  # 1 GBP = 4.55 QAR
    'KWD': 0.41,  # 1 GBP = 0.38 KWD
    'GBP': 1.00,
}

COUNTRIES = {
    'uk': {'name': 'UK', 'currency': 'GBP'},
    'kw': {'name': 'Kuwait', 'currency': 'KWD'},
    'ae': {'name': 'United Arab Emirates', 'currency': 'AED'},
    'sa': {'name': 'Saudi Arabia', 'currency': 'SAR'},
    'qa': {'name': 'Qatar', 'currency': 'QAR'},
    'us': {'name': 'USA', 'currency': 'USD'},
    'ca': {'name': 'Canada', 'currency': 'CAD'},
}


# --- Helper Functions ---
def get_rounded_price(base_price_gbp: int, target_currency: str) -> int | None:
    """Converts a GBP price using a fixed rate and rounds it nicely."""
    rate = RATES.get(target_currency)
    if not rate:
        logger.error(f"No rate found for currency: {target_currency}")
        return None

    converted = base_price_gbp * rate

    # Nice rounding logic
    if converted < 20:
        return int(ceil(converted))  # Round up to the nearest whole number
    else:
        return int(5 * ceil(converted / 5))  # Round up to the nearest 5


# --- Main Bot Functions ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts or restarts the conversation and asks for the user's country."""
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
    """Displays the main services menu. Can be called from different points."""
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
    """Stores the selected country and shows the service menu."""
    query = update.callback_query
    country_code = query.data.split('_')[1]
    context.user_data['country'] = COUNTRIES[country_code]
    return await show_services_menu(update, context)


# --- Service 1: Assignment Help ---
async def request_assignment_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Please upload a file, an image, or type a description of the assignment.\n\nTo go back, press /cancel.")
    return AWAITING_ASSIGNMENT


async def handle_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_country = context.user_data.get('country', {'name': 'Unknown'})['name']
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID,
                                   text=f"🔔 *New Assignment*\n\n*From:* {user.first_name} (`{user.id}`)\n*Country:* {user_country}",
                                   parse_mode='Markdown')
    await context.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=update.message.chat_id,
                                      message_id=update.message.message_id)
    await update.message.reply_text("✅ Thank you! Your assignment has been sent. A tutor will contact you shortly.")
    return ConversationHandler.END


# --- Service 2 & 3: Lessons & Tutor Connection ---
async def show_tutor_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the menu for 'Connect with Tutor'."""
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
    """Handles the direct Telegram connection request."""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_country = context.user_data.get('country', {'name': 'Unknown'})['name']

    # --- THIS IS THE MODIFIED PART ---
    # Create a special deep-link that opens a chat with the user when clicked.
    user_chat_link = f"tg://user?id={user.id}"

    # Notify Admin with the clickable link
    admin_text = (
        f"🔔 *Direct Connection Request*\n\n"
        f"User *{user.first_name}* from *{user_country}* wants to connect directly.\n\n"
        f"➡️ [Click here to chat with {user.first_name}]({user_chat_link})"
    )
    # --- END OF MODIFICATION ---

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text, parse_mode='Markdown')

    # Inform User
    await query.edit_message_text(
        "✅ The admin has been notified!\n\nA tutor will contact you directly on Telegram shortly.")
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


# --- Service 4: Price Info ---
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
        f"ℹ️ *Info*\n"
        f"— Lessons are online via Zoom.\n"
        f"— UK flexible payment options.\n"
        f"— Completion certificates available."
    )
    keyboard = [[InlineKeyboardButton("⬅️ Back to Services", callback_data='back_to_services')]]
    await query.edit_message_text(text=price_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SELECTING_TUTOR_OPTION  # Go to a state that can handle the back button


# --- General ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled. Type /start to begin again.",
                                    reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


# --- Main Execution ---
def main() -> None:
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        logger.error("FATAL: TELEGRAM_BOT_TOKEN or ADMIN_CLIENT_ID not found in environment variables!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

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
            AWAITING_ASSIGNMENT: [
                MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, handle_assignment)],
            AWAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AWAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            AWAITING_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalise_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    print("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()