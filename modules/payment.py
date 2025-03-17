import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)
from modules.payment_calculator import PaymentCalculator
from modules.leave_request import LeaveRequestHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for the conversation
SELECT_MOBILE, SELECT_PAYMENT, SELECT_GUARANTEE, SELECT_MONTHS = range(4)

class BotHandler:
    def __init__(self, mobile_models, payment_options, guarantee_options, installment_months, interest_rates):
        self.mobile_models = mobile_models
        self.payment_options = payment_options
        self.guarantee_options = guarantee_options
        self.installment_months = installment_months
        self.interest_rates = interest_rates
        self.payment_calculator = PaymentCalculator(mobile_models, payment_options, guarantee_options, installment_months, interest_rates)

    async def payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Payment command handler."""
        logger.info(f"User {update.effective_user.id} started the payment process.")
        return await self.start_plan_selection(update, context)  # Directly start payment calculation

    async def start_plan_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the mobile selection process."""
        keyboard = [[model] for model in self.mobile_models.keys()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("📱 لطفاً مدل موبایل مورد نظر خود را انتخاب کنید:", reply_markup=reply_markup)
        return SELECT_MOBILE

    async def select_mobile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save the selected mobile model and ask for payment percentage."""
        selected_mobile = update.message.text
        logger.info(f"User {update.effective_user.id} selected mobile model: {selected_mobile}")

        if selected_mobile not in self.mobile_models:
            logger.warning(f"Invalid mobile model selected by user {update.effective_user.id}: {selected_mobile}")
            await update.message.reply_text("❌ مدل نامعتبر است. لطفاً دوباره /payment را وارد کنید.")
            return ConversationHandler.END

        context.user_data["mobile_model"] = selected_mobile
        context.user_data["mobile_price"] = self.mobile_models[selected_mobile]

        keyboard = [[option] for option in self.payment_options]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("💰 چه مقدار از قیمت را می‌خواهید پیش‌پرداخت کنید؟", reply_markup=reply_markup)
        return SELECT_PAYMENT

    async def select_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save payment percentage and ask for guarantee type (چک or سفته)."""
        payment_percentage = update.message.text
        logger.info(f"User {update.effective_user.id} selected payment percentage: {payment_percentage}")

        if payment_percentage not in self.payment_options:
            logger.warning(f"Invalid payment percentage selected by user {update.effective_user.id}: {payment_percentage}")
            await update.message.reply_text("❌ مقدار پیش‌پرداخت نامعتبر است. لطفاً دوباره /payment را وارد کنید.")
            return ConversationHandler.END

        context.user_data["upfront_percentage"] = int(payment_percentage.strip('%')) / 100
        context.user_data["upfront_amount"] = context.user_data["mobile_price"] * context.user_data["upfront_percentage"]
        context.user_data["remaining_balance"] = context.user_data["mobile_price"] - context.user_data["upfront_amount"]

        # Apply extra price adjustments based on conditions
        mobile_price = context.user_data["mobile_price"]
        payment_percentage = int(payment_percentage.strip('%'))

        keyboard = [[option] for option in self.guarantee_options]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("📜 لطفاً نوع ضمانت (چک یا سفته) را انتخاب کنید:", reply_markup=reply_markup)
        return SELECT_GUARANTEE

    async def select_guarantee(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save guarantee type and ask for installment months."""
        guarantee_type = update.message.text
        logger.info(f"User {update.effective_user.id} selected guarantee type: {guarantee_type}")

        if guarantee_type not in self.guarantee_options:
            logger.warning(f"Invalid guarantee type selected by user {update.effective_user.id}: {guarantee_type}")
            await update.message.reply_text("❌ ضمانت نامعتبر است. لطفاً دوباره /payment را وارد کنید.")
            return ConversationHandler.END

        context.user_data["guarantee_type"] = guarantee_type

        # Apply extra price adjustments based on guarantee and payment percentage
        mobile_price = context.user_data["mobile_price"]
        payment_percentage = context.user_data["upfront_percentage"] * 100  # Convert back to percentage for logic

        if 50000000 <= mobile_price <= 70000000:
            if payment_percentage == 40 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 8000000
            elif payment_percentage == 40 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 9000000
            elif payment_percentage == 50 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 7000000
            elif payment_percentage == 50 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 8000000
            elif payment_percentage == 60 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 6000000
            elif payment_percentage == 60 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 7000000
            elif payment_percentage == 70 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 5000000
            elif payment_percentage == 70 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 6000000
            elif payment_percentage == 80 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 4000000

        elif 70000000 < mobile_price <= 100000000:
            if payment_percentage == 40 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 9000000
            elif payment_percentage == 40 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 10000000
            elif payment_percentage == 50 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 8000000
            elif payment_percentage == 50 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 9000000
            elif payment_percentage == 60 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 6000000
            elif payment_percentage == 60 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 7000000
            elif payment_percentage == 70 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 5000000
            elif payment_percentage == 70 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 6000000
            elif payment_percentage == 80 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 4000000
            elif payment_percentage == 80 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 5000000

        elif 100000001 <= mobile_price <= 150000001:
            if payment_percentage == 40 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 12000000
            elif payment_percentage == 40 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 13000000
            elif payment_percentage == 50 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 11000000
            elif payment_percentage == 50 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 12000000
            elif payment_percentage == 60 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 10000000
            elif payment_percentage == 60 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 11000000
            elif payment_percentage == 70 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 9000000
            elif payment_percentage == 70 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 10000000
            elif payment_percentage == 80 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 8000000
            elif payment_percentage == 80 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 9000000

        elif mobile_price > 150000000:
            # New condition for prices greater than 150,000,000
            if payment_percentage == 40 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 16000000
            elif payment_percentage == 40 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 17000000
            elif payment_percentage == 50 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 16000000
            elif payment_percentage == 50 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 16000000
            elif payment_percentage == 60 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 14000000
            elif payment_percentage == 60 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 15000000
            elif payment_percentage == 70 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 13000000
            elif payment_percentage == 70 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 14000000
            elif payment_percentage == 80 and guarantee_type == "چک":
                context.user_data["mobile_price"] += 12000000
            elif payment_percentage == 80 and guarantee_type == "سفته":
                context.user_data["mobile_price"] += 13000000


        keyboard = [[months] for months in self.installment_months]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text("📆 طی چند ماه می‌خواهید مبلغ باقی‌مانده را پرداخت کنید؟ (۲ تا ۶ ماه)", reply_markup=reply_markup)
        return SELECT_MONTHS

    async def select_months(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save installment months, calculate payments, and display summary."""
        months = update.message.text
        logger.info(f"User {update.effective_user.id} selected installment months: {months}")

        if months not in self.installment_months:
            logger.warning(f"Invalid installment months selected by user {update.effective_user.id}: {months}")
            await update.message.reply_text("❌ مدت اقساط نامعتبر است. لطفاً دوباره /payment را وارد کنید.")
            return ConversationHandler.END

        context.user_data["installment_months"] = int(months)

        # Use PaymentCalculator to calculate payments
        response = self.payment_calculator.calculate_payments(context.user_data)
        await update.message.reply_text(response)
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation."""
        logger.info(f"User {update.effective_user.id} canceled the operation.")
        await update.message.reply_text("❌ عملیات لغو شد.")
        return ConversationHandler.END
