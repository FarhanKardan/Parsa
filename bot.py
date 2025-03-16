from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes
from modules.payment import BotHandler
from modules.admin import AdminHandler
from modules.leave_request import LeaveRequestHandler
from modules.box import BoxManagerBot  # Import the BoxManagerBot class
import config

# Define constants
MOBILE_MODELS = {
    "iPhone 16 Pro Max 1TB": 230000000,
    "iPhone 16 Pro Max 512GB": 183000000,
    "iPhone 16 Pro Max 256GB": 165000000,
    "iPhone 16 Pro 512GB": 0,  # Verify this price; it seems incorrect
    "iPhone 16 Pro 256GB": 160000000,
    "iPhone 16 256GB": 111000000,
    "iPhone 16 128GB": 880000000,  # Verify this price; it seems unusually high
    "iPhone 13 256GB": 0,  # Verify this price
    "iPhone 13 128GB": 60000000,
    "S24 Ultra 512GB": 0,  # Verify this price
    "S24 Ultra 256GB": 100000000,
    "S24 FE 256GB": 47000000
}

PAYMENT_OPTIONS = ["40%", "50%", "60%", "70%", "80%"]
GUARANTEE_OPTIONS = ["چک", "سفته"]
INSTALLMENT_MONTHS = [str(i) for i in range(2, 7)]
INTEREST_RATES = {
    ("40%", "چک"): 0.05,
    ("40%", "سفته"): 0.07,
    ("50%", "چک"): 0.045,
    ("50%", "سفته"): 0.06,
    ("60%", "چک"): 0.04,
    ("60%", "سفته"): 0.055,
    ("70%", "چک"): 0.035,
    ("70%", "سفته"): 0.04,
    ("80%", "چک"): 0.025,
    ("80%", "سفته"): 0.035
}
ADMIN_USER_IDS = [6463294729, 61002957, 618685441, 210610395]  # Replace with actual admin user IDs

# Define states for the conversation
SELECT_MOBILE, SELECT_PAYMENT, SELECT_GUARANTEE, SELECT_MONTHS = range(4)

# Define states for leave request conversation
ASK_DATE, ASK_REASON = range(2)

class MainHandler:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = (
            "👋 سلام! به ربات خوش آمدید.\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:\n\n"
            "📱 /payment - محاسبه پرداخت اقساطی\n"
            "📅 /request_leave - درخواست مرخصی\n"
            "📦 /add_box - افزودن جعبه جدید\n"
            "📦 /update_box_category - به‌روزرسانی دسته‌بندی جعبه\n"
            "📦 /get_box_details - دریافت جزئیات جعبه\n"
            "📦 /remove_box - حذف جعبه\n\n"
            "❌ /cancel - لغو عملیات فعلی"
        )
        await update.message.reply_text(welcome_message)

def main():
    """Main function to start the bot."""
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Initialize handlers
    bot_handler = BotHandler(MOBILE_MODELS, PAYMENT_OPTIONS, GUARANTEE_OPTIONS, INSTALLMENT_MONTHS, INTEREST_RATES)
    admin_handler = AdminHandler(MOBILE_MODELS, ADMIN_USER_IDS)
    leave_request_handler = LeaveRequestHandler()  # Initialize LeaveRequestHandler
    main_handler = MainHandler()  # Initialize MainHandler
    box_manager_handler = BoxManagerBot()  # Initialize BoxManagerBot

    # Register the /start command as the default handler
    application.add_handler(CommandHandler("start", main_handler.start))

    # Conversation handler for selecting a plan (Payment Calculation)
    plan_selection_handler = ConversationHandler(
        entry_points=[CommandHandler("payment", bot_handler.payment)],
        states={
            SELECT_MOBILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.select_mobile)],
            SELECT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.select_payment)],
            SELECT_GUARANTEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.select_guarantee)],
            SELECT_MONTHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handler.select_months)],
        },
        fallbacks=[CommandHandler("cancel", bot_handler.cancel)],
    )

    # Conversation handler for leave requests
    leave_request_conversation = ConversationHandler(
        entry_points=[CommandHandler("request_leave", leave_request_handler.start_request)],
        states={
            ASK_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, leave_request_handler.receive_date)],
            ASK_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, leave_request_handler.receive_reason)],
        },
        fallbacks=[CommandHandler("cancel", leave_request_handler.cancel)],
    )

    # Register other handlers
    application.add_handler(plan_selection_handler)  # Payment Calculation
    application.add_handler(leave_request_conversation)  # Leave Request
    application.add_handler(CallbackQueryHandler(leave_request_handler.process_manager_response))
    application.add_handler(CommandHandler("admin_add_phone", admin_handler.admin_add_phone))
    application.add_handler(CommandHandler("admin_edit_phone_price", admin_handler.admin_edit_phone_price))
    application.add_handler(CommandHandler("admin_remove_phone", admin_handler.admin_remove_phone))

    # Add box-related handlers
    for handler in box_manager_handler.get_handlers():
        application.add_handler(handler)

    application.run_polling()

if __name__ == "__main__":
    main()
