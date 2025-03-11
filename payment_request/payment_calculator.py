from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)
import config

# Define states for the conversation
SELECT_MOBILE, SELECT_PAYMENT, SELECT_GUARANTEE, SELECT_MONTHS, ADMIN_COMMANDS = range(5)

# Available mobile models and prices
MOBILE_MODELS = {
    "iPhone 16": 80000000,
    "Samsung Galaxy S24": 1000,
    "Google Pixel 9": 900
}

# Payment options
PAYMENT_OPTIONS = ["40%", "50%", "60%", "70%", "80%"]

# Guarantee options
GUARANTEE_OPTIONS = ["چک", "سفته"]

# Installment periods (only 2-12 months allowed)
INSTALLMENT_MONTHS = [str(i) for i in range(2, 7)]

# Interest rates based on upfront payment and guarantee type
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

# Admin user ID (update with the actual Telegram user ID of the admin)
ADMIN_USER_IDS = [6463294729, 64632947294]  # Replace with the actual admin user ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("خوش آمدید! برای انتخاب طرح اقساطی از /choose_plan استفاده کنید.")

async def start_plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the mobile selection process."""
    keyboard = [[model] for model in MOBILE_MODELS.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("📱 لطفاً مدل موبایل مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
    return SELECT_MOBILE

async def select_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the selected mobile model and ask for payment percentage."""
    selected_mobile = update.message.text

    if selected_mobile not in MOBILE_MODELS:
        await update.message.reply_text("❌ مدل نامعتبر است. لطفاً دوباره /choose_plan را وارد کنید.")
        return ConversationHandler.END

    context.user_data["mobile_model"] = selected_mobile
    context.user_data["mobile_price"] = MOBILE_MODELS[selected_mobile]

    keyboard = [[option] for option in PAYMENT_OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("💰 چه مقدار از قیمت را می‌خواهید پیش‌پرداخت کنید؟", reply_markup=reply_markup)
    return SELECT_PAYMENT

async def select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save payment percentage and ask for guarantee type (چک or سفته)."""
    payment_percentage = update.message.text

    if payment_percentage not in PAYMENT_OPTIONS:
        await update.message.reply_text("❌ مقدار پیش‌پرداخت نامعتبر است. لطفاً دوباره /choose_plan را وارد کنید.")
        return ConversationHandler.END

    context.user_data["upfront_percentage"] = int(payment_percentage.strip('%')) / 100
    context.user_data["upfront_amount"] = context.user_data["mobile_price"] * context.user_data["upfront_percentage"]
    context.user_data["remaining_balance"] = context.user_data["mobile_price"] - context.user_data["upfront_amount"]

    keyboard = [[option] for option in GUARANTEE_OPTIONS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("📜 لطفاً نوع ضمانت (چک یا سفته) را انتخاب کنید:", reply_markup=reply_markup)
    return SELECT_GUARANTEE

async def select_guarantee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save guarantee type and ask for installment months."""
    guarantee_type = update.message.text

    if guarantee_type not in GUARANTEE_OPTIONS:
        await update.message.reply_text("❌ ضمانت نامعتبر است. لطفاً دوباره /choose_plan را وارد کنید.")
        return ConversationHandler.END

    context.user_data["guarantee_type"] = guarantee_type

    keyboard = [[months] for months in INSTALLMENT_MONTHS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("📆 طی چند ماه می‌خواهید مبلغ باقی‌مانده را پرداخت کنید؟ (۲ تا ۶ ماه)", reply_markup=reply_markup)
    return SELECT_MONTHS

async def select_months(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save installment months, calculate payments, and display summary."""
    months = update.message.text

    if months not in INSTALLMENT_MONTHS:
        await update.message.reply_text("❌ مدت اقساط نامعتبر است. لطفاً دوباره /choose_plan را وارد کنید.")
        return ConversationHandler.END

    context.user_data["installment_months"] = int(months)

    # Get stored data
    mobile_model = context.user_data["mobile_model"]
    mobile_price = context.user_data["mobile_price"]
    upfront_amount = context.user_data["upfront_amount"]
    remaining_balance = context.user_data["remaining_balance"]
    payment_percentage = f"{int(context.user_data['upfront_percentage'] * 100)}%"
    guarantee_type = context.user_data["guarantee_type"]

    # Get interest rate based on payment and guarantee
    interest_rate = INTEREST_RATES.get((payment_percentage, guarantee_type), 0)

    # Calculate interest and monthly payments
    total_interest = remaining_balance * interest_rate * context.user_data["installment_months"]
    total_amount_due = remaining_balance + total_interest
    monthly_payment = total_amount_due / context.user_data["installment_months"]

    response = (
    f"✅ شما انتخاب کردید: {mobile_model}\n"
    f"💰 قیمت: {mobile_price:,.2f}\n"
    f"💵 پیش‌پرداخت: {upfront_amount:,.2f} ({payment_percentage})\n"
    f"🛒 مبلغ باقی‌مانده: ${remaining_balance:,.2f}\n"
    f"📜 نوع ضمانت: {guarantee_type}\n"
    f"📆 دوره اقساط: {months} ماه\n"
    f"💲 نرخ سود ماهانه: {interest_rate * 100:.1f}%\n"
    f"📈 کل سود: {total_interest:,.2f}\n"
    f"💳 مبلغ پرداختی ماهانه: {monthly_payment:,.2f}\n"
    f"💸 مجموع مبلغ پرداختی: {total_amount_due:,.2f}"
)


    await update.message.reply_text(response)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation."""
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END


async def admin_add_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle adding a mobile model (admin only)."""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ شما دسترسی به این بخش ندارید.")
        return

    command = update.message.text.strip().split(" ", 1)
    if len(command) < 2:
        await update.message.reply_text("❌ دستور نامعتبر است. لطفاً دستور صحیح را وارد کنید.")
        return

    argument = command[1]
    try:
        model, price = argument.split(", ")
        price = float(price)
        MOBILE_MODELS[model] = price
        await update.message.reply_text(f"✅ مدل {model} به همراه قیمت ${price} اضافه شد.")
    except ValueError:
        await update.message.reply_text("❌ فرمت اشتباه است. لطفاً از فرمت صحیح استفاده کنید: /admin_add_phone <مدل, قیمت>")

async def admin_edit_phone_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle editing the price of a mobile model (admin only)."""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ شما دسترسی به این بخش ندارید.")
        return

    command = update.message.text.strip().split(" ", 1)
    if len(command) < 2:
        await update.message.reply_text("❌ دستور نامعتبر است. لطفاً دستور صحیح را وارد کنید.")
        return

    argument = command[1]
    try:
        model, new_price = argument.split(", ")
        new_price = float(new_price)
        if model in MOBILE_MODELS:
            MOBILE_MODELS[model] = new_price
            await update.message.reply_text(f"✅ قیمت مدل {model} به ${new_price} تغییر یافت.")
        else:
            await update.message.reply_text("❌ مدل مورد نظر یافت نشد.")
    except ValueError:
        await update.message.reply_text("❌ فرمت اشتباه است. لطفاً از فرمت صحیح استفاده کنید: /admin_edit_phone_price <مدل, قیمت>")

async def admin_remove_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle removing a mobile model (admin only)."""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ شما دسترسی به این بخش ندارید.")
        return

    command = update.message.text.strip().split(" ", 1)
    if len(command) < 2:
        await update.message.reply_text("❌ دستور نامعتبر است. لطفاً دستور صحیح را وارد کنید.")
        return

    model = command[1]
    if model in MOBILE_MODELS:
        del MOBILE_MODELS[model]
        await update.message.reply_text(f"✅ مدل {model} حذف شد.")
    else:
        await update.message.reply_text("❌ مدل مورد نظر یافت نشد.")

def main():
    """Main function to start the bot."""
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Conversation handler for selecting a plan
    plan_selection_handler = ConversationHandler(
        entry_points=[CommandHandler("choose_plan", start_plan_selection)],
        states={
            SELECT_MOBILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_mobile)],
            SELECT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_payment)],
            SELECT_GUARANTEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_guarantee)],
            SELECT_MONTHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_months)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Command handlers for admin commands
    admin_add_phone_handler = CommandHandler("admin_add_phone", admin_add_phone)
    admin_edit_phone_price_handler = CommandHandler("admin_edit_phone_price", admin_edit_phone_price)
    admin_remove_phone_handler = CommandHandler("admin_remove_phone", admin_remove_phone)

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(plan_selection_handler)
    application.add_handler(admin_add_phone_handler)
    application.add_handler(admin_edit_phone_price_handler)
    application.add_handler(admin_remove_phone_handler)

    application.run_polling()

if __name__ == "__main__":
    main()

