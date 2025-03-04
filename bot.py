import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)
from handlers import (
    start,
    start_request,
    receive_date,
    receive_reason,
    cancel,
    process_manager_response,
)
import config  # Import config file for the configuration
from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDate

# Define conversation states
ASK_DATE, ASK_REASON = range(2)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function to receive the leave date and validate it
from datetime import timedelta
from persiantools.jdatetime import JalaliDate
from telegram import Update
from telegram.ext import CallbackContext

# Function to receive the leave date and validate it based on Jalali inputs
async def receive_date(update: Update, context: CallbackContext):
    date_str = update.message.text
    try:
        # Parse the user's input as a Jalali date
        requested_date = JalaliDate.fromisoformat(date_str)
        today = JalaliDate.today()

        # Calculate 2 and 12 days in the Jalali calendar
        two_days_later = today + timedelta(days=2)
        fourteen_days_later = today + timedelta(days=12)

        # Validate the requested date against the range
        if two_days_later <= requested_date <= fourteen_days_later:
            # Convert back to Gregorian to store in context if needed
            context.user_data["date"] = requested_date.to_gregorian().strftime("%Y-%m-%d")
            await update.message.reply_text("تاریخ ثبت شد! حالا لطفاً دلیل مرخصی خود را وارد کنید:")
            return ASK_REASON
        else:
            await update.message.reply_text(
                "شما تنها می‌توانید درخواست مرخصی بین ۲ تا ۱۲ روز از امروز ارسال کنید. لطفاً یک تاریخ در این بازه انتخاب کنید."
            )
            return ASK_DATE
    except ValueError:
        await update.message.reply_text("فرمت تاریخ نادرست است. لطفاً از فرمت YYYY-MM-DD استفاده کنید.")
        return ASK_DATE



# Main function to start the bot
def main():
    logger.info("Starting the bot...")

    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("request_leave", start_request)],
        states={
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],
            ASK_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reason)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(process_manager_response))

    application.add_handler(conv_handler)

    logger.info("Bot is now running...")
    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
