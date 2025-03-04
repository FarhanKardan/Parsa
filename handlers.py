import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
from db_operations import add_leave_request, update_request_status, get_approved_requests_by_class, has_pending_or_approved_requests
from utils import validate_date, is_employee, is_manager, is_operations_employee, is_sales_employee
from config import OPERATIONS_EMPLOYEES, SALES_EMPLOYEES, AUTHORIZED_MANAGER_IDS
from utils import get_employee_details
from persiantools.jdatetime import JalaliDate
from datetime import datetime
logger = logging.getLogger(__name__)

# Define conversation states
ASK_DATE, ASK_REASON = range(2)

# Handlers
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    # Ensure the user is authorized
    if user_id not in OPERATIONS_EMPLOYEES and user_id not in SALES_EMPLOYEES and user_id not in AUTHORIZED_MANAGER_IDS:
        await update.message.reply_text("شما مجاز به تعامل با این ربات نیستید.")
        return

    logger.info(f"Bot started by user: {user_id}")
    await update.message.reply_text(
        "به ربات مدیریت کارکنان خوش آمدید! 🎉\n\n"
        "دستورات:\n"
        "/request_leave - ارسال درخواست مرخصی\n"
    )

async def start_request(update: Update, context: CallbackContext):
    employee_id = update.message.from_user.id

    # Check if the employee is in the Operations or Sales group
    if is_operations_employee(employee_id):
        employee_class = "Operations"
        employee_role = "Operations"
    elif is_sales_employee(employee_id):
        employee_class = "Sales"
        employee_role = "Sales"
    else:
        # If the employee is neither Operations nor Sales
        await update.message.reply_text("شما مجاز به ارسال درخواست مرخصی نیستید.")
        return ConversationHandler.END

    # Check if the employee has already submitted a leave request (approved or pending)
    existing_request = has_pending_or_approved_requests(employee_id)
    if existing_request:
        await update.message.reply_text("شما در حال حاضر یک درخواست مرخصی در حال انتظار دارید. نمی‌توانید درخواست دیگری ارسال کنید.")
        return ConversationHandler.END

    # Check if any employee with the same role has an approved leave request
    approved_requests = get_approved_requests_by_class(employee_class)
    same_role_approved_requests = [r for r in approved_requests if r["role"] == employee_role]
    
    if same_role_approved_requests:
        await update.message.reply_text(f"یکی دیگر از کارکنان در نقش {employee_role} قبلاً برای مرخصی تأیید شده است. شما نمی‌توانید درخواست مرخصی ارسال کنید.")
        return ConversationHandler.END

    # If no approved requests or existing leave, proceed with the leave request
    await update.message.reply_text("لطفاً تاریخ مرخصی خود را وارد کنید (فرمت: YYYY-MM-DD):")
    return ASK_DATE


async def receive_date(update: Update, context: CallbackContext):
    date = update.message.text
    logger.info(f"User {update.message.from_user.id} entered date: {date}")
    
    if validate_date(date):
        context.user_data["date"] = date
        await update.message.reply_text("تاریخ ثبت شد! حالا لطفاً دلیل مرخصی خود را وارد کنید:")
        return ASK_REASON
    else:
        logger.error(f"Invalid date format received from {update.message.from_user.id}: {date}")
        await update.message.reply_text(
            "فرمت تاریخ نادرست است. لطفاً از فرمت YYYY-MM-DD استفاده کنید. به صورت پیش‌فرض، تاریخ فعلی انتخاب خواهد شد.\n"
            "اگر مایل هستید، می‌توانید دوباره یک تاریخ وارد کنید:"
        )
        # Set a default date, e.g., today's date
        default_date = datetime.now().strftime("%Y-%m-%d")
        context.user_data["date"] = default_date
        
        # Send a follow-up message to proceed with the next step
        await update.message.reply_text(
            f"تاریخ پیش‌فرض انتخاب شده: {default_date}\n"
            "حال لطفاً دلیل مرخصی خود را وارد کنید:"
        )
        return ASK_REASON

from datetime import datetime
from persiantools.jdatetime import JalaliDate

async def receive_reason(update: Update, context: CallbackContext):
    reason = update.message.text
    user_id = update.message.from_user.id
    date_str = context.user_data.get("date")

    # Convert the string to a datetime object
    requested_date_gregorian = datetime.strptime(date_str, "%Y-%m-%d")

    # Convert the Gregorian date to Jalali
    requested_date_jalali = JalaliDate.to_jalali(requested_date_gregorian)

    # Get the day of the week in Jalali
    day_of_week = requested_date_jalali.strftime('%A')  # Gets the Persian day of the week

    # Fetch employee details
    employee_details = get_employee_details(user_id)
    employee_name = employee_details["name"]
    employee_family = employee_details["family"]
    employee_role = employee_details["role"]

    # Add the leave request to the database
    request_id = add_leave_request(user_id, date_str, reason)
    logger.info(f"Leave request submitted by {user_id} for date {date_str} with reason: {reason}")

    # Request details to send to the manager
    request_details = (
        f"نام کارمند: {employee_name} {employee_family}\n"
        f"نقش: {employee_role}\n"
        f"شناسه کارمند: {user_id}\n"
        f"تاریخ: {requested_date_jalali} ({day_of_week})\n"
        f"دلیل: {reason}"
    )

    # Send the leave request details to the manager (or elsewhere)
    await update.message.reply_text(request_details)

    # Send the request to the manager
    manager_chat_id = AUTHORIZED_MANAGER_IDS[0]  # For simplicity, using the first manager ID
    await send_request_to_manager(manager_chat_id, request_id, request_details, context)

    await update.message.reply_text("درخواست مرخصی شما ارسال شده و برای تأیید به مدیر ارسال گردید.")
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    logger.info(f"User {update.message.from_user.id} cancelled the leave request process.")
    await update.message.reply_text("فرآیند درخواست مرخصی لغو شد.")
    return ConversationHandler.END

# Updated send_request_to_manager function
async def send_request_to_manager(manager_chat_id: int, request_id: str, request_details: str, context: CallbackContext):
    context.user_data["request_id"] = request_id
    keyboard = [
        [
            InlineKeyboardButton("تأیید", callback_data=f"approve_{request_id}"),
            InlineKeyboardButton("رد", callback_data=f"reject_{request_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=manager_chat_id,
        text=f"درخواست مرخصی جدید دریافت شد:\n\n{request_details}\n\nلطفاً درخواست را تأیید یا رد کنید.",
        reply_markup=reply_markup
    )

from persiantools.jdatetime import JalaliDate

async def process_manager_response(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Extract action and request_id from callback data
    action, request_id = query.data.split("_")
    decision = "تأیید" if action == "approve" else "رد"

    # Update the request status in the database
    request_data = update_request_status(request_id, decision)  # Assuming it returns the updated data, including employee_id
    if request_data:
        employee_id = request_data["employee_id"]
        employee_name = request_data["name"]
        employee_date = request_data["date"]

        # Convert Gregorian date to Jalali
        requested_date_gregorian = datetime.strptime(employee_date, "%Y-%m-%d")
        requested_date_jalali = JalaliDate.to_jalali(requested_date_gregorian)

        # Notify the manager about the action
        await query.message.reply_text(f"درخواست {request_id} {decision} شد.")

        # Avoid sending multiple notifications by checking if a message has already been sent
        try:
            decision_message = (
                f"سلام {employee_name},\n\n"
                f"درخواست مرخصی شما برای تاریخ {requested_date_jalali} توسط مدیر {decision} شد."
            )
            # Check if the notification has already been sent (based on employee_id or another flag)
            # We can store sent message info in a cache or database flag to avoid repetition
            # For simplicity, assume `employee_id` is unique and we only send one message per request.
            
            # Send the notification only once
            if not hasattr(context.chat_data, "notified_employees"):
                context.chat_data["notified_employees"] = set()
                
            if employee_id not in context.chat_data["notified_employees"]:
                await context.bot.send_message(chat_id=employee_id, text=decision_message)
                context.chat_data["notified_employees"].add(employee_id)  # Mark as notified
                logger.info(f"Notification sent to employee {employee_id} about the {decision} decision.")
            else:
                logger.info(f"Notification already sent to employee {employee_id}. Skipping.")
        except Exception as e:
            logger.error(f"Error sending notification to employee {employee_id}: {e}")
    else:
        await query.message.reply_text("خطا در پردازش درخواست. لطفاً دوباره تلاش کنید.")

