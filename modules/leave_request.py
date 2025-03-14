import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from db_operations import add_leave_request, update_request_status, has_pending_or_approved_requests
from utils import is_operations_employee, is_sales_employee, get_employee_details
from config import OPERATIONS_EMPLOYEES, SALES_EMPLOYEES, AUTHORIZED_MANAGER_IDS
from persiantools.jdatetime import JalaliDate
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Define conversation states
ASK_DATE, ASK_REASON = range(2)

class LeaveRequestHandler:
    def __init__(self):
        pass

    async def start(self, update: Update, context: CallbackContext):
        """Start command handler."""
        user_id = update.message.from_user.id

        if user_id not in OPERATIONS_EMPLOYEES and user_id not in SALES_EMPLOYEES and user_id not in AUTHORIZED_MANAGER_IDS:
            await update.message.reply_text("شما مجاز به تعامل با این ربات نیستید.")
            return

        await update.message.reply_text(
            "به ربات مدیریت کارکنان خوش آمدید! 🎉\n\n"
            "/request_leave - ارسال درخواست مرخصی\n"
            "/cancel - لغو عملیات جاری"
        )

    async def start_request(self, update: Update, context: CallbackContext):
        """Start the leave request process."""
        user_id = update.message.from_user.id

        # Check if the user is allowed to request leave
        if not (is_operations_employee(user_id) or is_sales_employee(user_id)):
            await update.message.reply_text("شما مجاز به ارسال درخواست مرخصی نیستید.")
            return ConversationHandler.END

        # Check if user has pending or approved requests
        if has_pending_or_approved_requests(user_id):
            await update.message.reply_text("شما در حال حاضر یک درخواست مرخصی در حال انتظار دارید.")
            return ConversationHandler.END

        await update.message.reply_text("لطفاً تاریخ مرخصی خود را وارد کنید (فرمت: YYYY-MM-DD):")
        return ASK_DATE

    async def receive_date(self, update: Update, context: CallbackContext):
        """Receive and validate the leave date."""
        date_str = update.message.text
        try:
            requested_date = JalaliDate.fromisoformat(date_str)
            today = JalaliDate.today()
            two_days_later = today + timedelta(days=2)
            fourteen_days_later = today + timedelta(days=12)

            if two_days_later <= requested_date <= fourteen_days_later:
                context.user_data["date"] = requested_date.to_gregorian().strftime("%Y-%m-%d")
                await update.message.reply_text("تاریخ ثبت شد! حالا لطفاً دلیل مرخصی خود را وارد کنید:")
                return ASK_REASON
            else:
                await update.message.reply_text("تاریخ باید بین ۲ تا ۱۲ روز از امروز باشد.")
                return ASK_DATE
        except ValueError:
            await update.message.reply_text("فرمت تاریخ نادرست است. لطفاً از فرمت YYYY-MM-DD استفاده کنید.")
            return ASK_DATE

    async def receive_reason(self, update: Update, context: CallbackContext):
        """Receive the reason for the leave request and send it to managers."""
        reason = update.message.text
        user_id = update.message.from_user.id
        date_str = context.user_data["date"]
        requested_date_jalali = JalaliDate.to_jalali(datetime.strptime(date_str, "%Y-%m-%d"))

        # Get employee details and save leave request
        employee_details = get_employee_details(user_id)
        request_id = add_leave_request(user_id, date_str, reason)

        request_details = (
            f"🧑‍💼 نام کارمند: {employee_details['name']} {employee_details['family']}\n"
            f"💼 نقش: {employee_details['role']}\n"
            f"📅 تاریخ درخواست مرخصی: {requested_date_jalali} ({requested_date_jalali.strftime('%A')})\n"
            f"📝 دلیل درخواست: {reason}\n\n"
            f"لطفاً درخواست مرخصی را تأیید یا رد کنید:"
        )
        for manager_chat_id in AUTHORIZED_MANAGER_IDS:
            await self.send_request_to_manager(manager_chat_id, request_id, request_details, context)

        await update.message.reply_text("درخواست مرخصی شما ارسال شده است.")
        return ConversationHandler.END

    async def send_request_to_manager(self, manager_chat_id: int, request_id: str, request_details: str, context: CallbackContext):
        """Send leave request to a manager with inline buttons for approval/rejection."""
        keyboard = [
            [InlineKeyboardButton("تأیید", callback_data=f"approve_{request_id}"),
             InlineKeyboardButton("رد", callback_data=f"reject_{request_id}")]
        ]
        await context.bot.send_message(
            chat_id=manager_chat_id,
            text=f"درخواست مرخصی جدید دریافت شد:\n\n{request_details}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def process_manager_response(self, update: Update, context: CallbackContext):
        """Handle manager's response to a leave request."""
        query = update.callback_query
        query.answer()

        action, request_id = query.data.split("_")
        decision = "تأیید" if action == "approve" else "رد"
        request_data = update_request_status(request_id, decision)

        if request_data:
            employee_id = request_data["employee_id"]
            employee_name = request_data["name"]
            employee_family = request_data["family"]
            employee_date = request_data["date"]

            requested_date_jalali = JalaliDate.to_jalali(datetime.strptime(employee_date, "%Y-%m-%d"))

            # Notify the employee
            decision_message = (
                f"سلام {employee_name},\n\n"
                f"درخواست مرخصی شما برای تاریخ {requested_date_jalali} توسط مدیر {decision} شد."
            )
            await context.bot.send_message(chat_id=employee_id, text=decision_message)

            # Notify other managers
            manager_notification = (
                f"📢 اطلاعیه به مدیران\n\n"
                f"درخواست مرخصی {employee_name} {employee_family} برای تاریخ {requested_date_jalali} "
                f"توسط یکی از مدیران {decision} شد."
            )

            for manager_id in AUTHORIZED_MANAGER_IDS:
                if manager_id != query.from_user.id:  # Don't send notification to the manager who made the decision
                    await context.bot.send_message(chat_id=manager_id, text=manager_notification)

            # Disable the keyboard by updating the message with no buttons
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup([]))

            # Confirm decision to the responding manager
            await query.message.reply_text(
                f"✅ درخواست مرخصی {employee_name} {employee_family}\n"
                f"📅 وضعیت: {decision}\n"
                f"✉️ مدیر محترم، تصمیم شما ثبت شد."
            )
        else:
            await query.message.reply_text("خطا در پردازش درخواست. لطفاً دوباره تلاش کنید.")

    async def cancel(self, update: Update, context: CallbackContext):
        """Cancel the leave request process."""
        await update.message.reply_text("فرآیند درخواست مرخصی لغو شد.")
        return ConversationHandler.END