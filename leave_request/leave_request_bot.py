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
from leave_request_handler import (
    start,
    start_request,
    receive_date,
    receive_reason,
    cancel,
    process_manager_response,
)
import config  
from db_operations import get_approved_leave_requests_by_jalali_month

# Define conversation states
ASK_DATE, ASK_REASON = range(2)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
