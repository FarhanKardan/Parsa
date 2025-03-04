import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from db_operations import insert_box, update_box_category, get_box_details, remove_box
from config import AUTHORIZED_USER_IDS  # A list of authorized user IDs

# Conversation states
BOX_ID, SHOP_CATEGORY = range(2)
UPDATE_BOX_ID, NEW_SHOP_CATEGORY = range(2, 4)
GET_BOX_ID = 5

# Setup logger
logger = logging.getLogger(__name__)

# Check if the user is authorized
async def check_authorization(update: Update):
    user_id = update.message.from_user.id
    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("شما مجاز به تعامل با این ربات نیستید.")
        return False
    return True

# Start the add_box conversation
async def start_add_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_authorization(update):
        return ConversationHandler.END

    await update.message.reply_text("لطفا شناسه جعبه را وارد کنید.")
    return BOX_ID

# Handle Box ID input
async def handle_box_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['box_id'] = update.message.text
    await update.message.reply_text(
        "شناسه جعبه دریافت شد! حالا لطفاً دسته‌بندی فروشگاه (انبار با گارانتی، انبار داخل شرکت، یا انبار بیرون) را وارد کنید."
    )
    return SHOP_CATEGORY

# Handle Shop Category input
async def handle_shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shop_category = update.message.text

    if shop_category not in ["انبار با گارانتی", "انبار داخل شرکت", "انبار بیرون"]:
        await update.message.reply_text(
            "دسته‌بندی نامعتبر است! لطفاً 'انبار با گارانتی'، 'انبار داخل شرکت' یا 'انبار بیرون' را وارد کنید."
        )
        return SHOP_CATEGORY

    box_id = context.user_data['box_id']
    if insert_box(box_id, shop_category):
        await update.message.reply_text(
            f"جعبه با شناسه {box_id} و دسته‌بندی فروشگاه {shop_category} با موفقیت اضافه شد",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "اضافه کردن جعبه با شکست مواجه شد. لطفاً دوباره تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END

# Start the update_box_category conversation
async def start_update_box_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_authorization(update):
        return ConversationHandler.END

    await update.message.reply_text(
        "لطفاً شناسه جعبه‌ای که می‌خواهید دسته‌بندی آن را به‌روزرسانی کنید وارد کنید."
    )
    return UPDATE_BOX_ID

# Handle Box ID input for updating
async def handle_update_box_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['update_box_id'] = update.message.text
    await update.message.reply_text(
        "شناسه جعبه دریافت شد! حالا لطفاً دسته‌بندی جدید فروشگاه (انبار با گارانتی، انبار داخل شرکت، یا انبار بیرون) را وارد کنید."
    )
    return NEW_SHOP_CATEGORY

# Handle Shop Category input for updating
async def handle_new_shop_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_shop_category = update.message.text

    if new_shop_category not in ["انبار با گارانتی", "انبار داخل شرکت", "انبار بیرون"]:
        await update.message.reply_text(
            "دسته‌بندی نامعتبر است! لطفاً 'انبار با گارانتی'، 'انبار داخل شرکت' یا 'انبار بیرون' را وارد کنید."
        )
        return NEW_SHOP_CATEGORY

    update_box_id = context.user_data['update_box_id']
    if update_box_category(update_box_id, new_shop_category):
        await update.message.reply_text(
            f"جعبه با شناسه {update_box_id} با موفقیت به دسته‌بندی {new_shop_category} به‌روزرسانی شد.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "به‌روزرسانی دسته‌بندی جعبه با شکست مواجه شد. لطفاً شناسه جعبه را بررسی کرده و دوباره تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END

# Start the get_box_details conversation
async def start_get_box_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_authorization(update):
        return ConversationHandler.END

    await update.message.reply_text("لطفاً شناسه جعبه را وارد کنید تا جزئیات آن را دریافت کنید.")
    return GET_BOX_ID

# Handle Box ID input for retrieving details
async def handle_get_box_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    box_id = update.message.text
    context.user_data['box_id'] = box_id

    # Retrieve box details from the database
    details = get_box_details(box_id)

    await update.message.reply_text(details, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Start the remove_box conversation
async def start_remove_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_authorization(update):
        return ConversationHandler.END

    await update.message.reply_text("لطفاً شناسه جعبه‌ای که می‌خواهید حذف کنید وارد کنید.")
    return GET_BOX_ID

# Handle Box ID input for removing
async def handle_remove_box_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    box_id = update.message.text
    context.user_data['box_id'] = box_id

    # Remove box from the database
    if remove_box(box_id):
        await update.message.reply_text(
            f"جعبه با شناسه {box_id} با موفقیت حذف شد.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "حذف جعبه با شکست مواجه شد. لطفاً شناسه جعبه را بررسی کرده و دوباره تلاش کنید.",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END

# Cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Command to show available commands and their descriptions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "خوش آمدید! دستورات زیر را برای استفاده از ربات می‌توانید وارد کنید:\n\n"
        "/start - نمایش این لیست دستورات\n"
        "/add_box - افزودن جعبه جدید به صورت مرحله به مرحله\n"
        "/get_box_details - دریافت جزئیات جعبه با شناسه آن\n"
        "/update_box_category - به‌روزرسانی دسته‌بندی فروشگاه جعبه موجود\n"
        "/remove_box - حذف جعبه از پایگاه داده با شناسه آن\n"
    )
    await update.message.reply_text(help_text)

# Handlers
add_box_handler = ConversationHandler(
    entry_points=[CommandHandler("add_box", start_add_box)],
    states={
        BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_box_id)],
        SHOP_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_shop_category)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

update_box_handler = ConversationHandler(
    entry_points=[CommandHandler("update_box_category", start_update_box_category)],
    states={
        UPDATE_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_box_id)],
        NEW_SHOP_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_shop_category)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

get_box_details_handler = ConversationHandler(
    entry_points=[CommandHandler("get_box_details", start_get_box_details)],
    states={
        GET_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_box_id)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

remove_box_handler = ConversationHandler(
    entry_points=[CommandHandler("remove_box", start_remove_box)],
    states={
        GET_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remove_box_id)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
