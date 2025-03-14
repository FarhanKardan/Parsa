from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from db_operations import insert_box, update_box_category, get_box_details, remove_box
from config import AUTHORIZED_USER_IDS  # A list of authorized user IDs
import logging
# Setup logger
logger = logging.getLogger(__name__)

# Define conversation states
class ConversationStates:
    BOX_ID, SHOP_CATEGORY = range(2)
    UPDATE_BOX_ID, NEW_SHOP_CATEGORY = range(2, 4)
    GET_BOX_ID = 5

# Define box categories
BOX_CATEGORIES = ["انبار با گارانتی", "انبار داخل شرکت", "انبار بیرون"]

class BoxManagerBot:
    def __init__(self):
        self.states = ConversationStates()

    # Check if the user is authorized
    async def check_authorization(self, update: Update):
        user_id = update.message.from_user.id
        if user_id not in AUTHORIZED_USER_IDS:
            await update.message.reply_text("شما مجاز به تعامل با این ربات نیستید.")
            return False
        return True

    # Start command to show available commands and their descriptions
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            "خوش آمدید! دستورات زیر را برای استفاده از ربات می‌توانید وارد کنید:\n\n"
            "/add_box - افزودن جعبه جدید به صورت مرحله به مرحله\n"
            "/get_box_details - دریافت جزئیات جعبه با شناسه آن\n"
            "/update_box_category - به‌روزرسانی دسته‌بندی فروشگاه جعبه موجود\n"
            "/remove_box - حذف جعبه از پایگاه داده با شناسه آن\n"
            "/cancel - لغو عملیات جاری در هر مرحله از گفتگو\n"
        )
        await update.message.reply_text(help_text)

    # Start the add_box conversation
    async def start_add_box(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_authorization(update):
            return ConversationHandler.END

        await update.message.reply_text("لطفاً شناسه جعبه را وارد کنید.")
        return self.states.BOX_ID

    # Handle Box ID input for adding
    async def handle_box_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['box_id'] = update.message.text

        # Show category selection keyboard
        keyboard = [BOX_CATEGORIES]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "شناسه جعبه دریافت شد! لطفاً دسته‌بندی فروشگاه را انتخاب کنید:",
            reply_markup=reply_markup,
        )
        return self.states.SHOP_CATEGORY

    # Handle Shop Category input for adding
    async def handle_shop_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        shop_category = update.message.text

        if shop_category not in BOX_CATEGORIES:
            await update.message.reply_text(
                "دسته‌بندی نامعتبر است! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup([BOX_CATEGORIES], one_time_keyboard=True, resize_keyboard=True),
            )
            return self.states.SHOP_CATEGORY

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
    async def start_update_box_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_authorization(update):
            return ConversationHandler.END

        await update.message.reply_text(
            "لطفاً شناسه جعبه‌ای که می‌خواهید دسته‌بندی آن را به‌روزرسانی کنید وارد کنید."
        )
        return self.states.UPDATE_BOX_ID

    # Handle Box ID input for updating
    async def handle_update_box_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['update_box_id'] = update.message.text

        # Show category selection keyboard
        keyboard = [BOX_CATEGORIES]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "شناسه جعبه دریافت شد! لطفاً دسته‌بندی جدید فروشگاه را انتخاب کنید:",
            reply_markup=reply_markup,
        )
        return self.states.NEW_SHOP_CATEGORY

    # Handle Shop Category input for updating
    async def handle_new_shop_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_shop_category = update.message.text

        if new_shop_category not in BOX_CATEGORIES:
            await update.message.reply_text(
                "دسته‌بندی نامعتبر است! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup([BOX_CATEGORIES], one_time_keyboard=True, resize_keyboard=True),
            )
            return self.states.NEW_SHOP_CATEGORY

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
    async def start_get_box_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_authorization(update):
            return ConversationHandler.END

        await update.message.reply_text("لطفاً شناسه جعبه را وارد کنید تا جزئیات آن را دریافت کنید.")
        return self.states.GET_BOX_ID

    # Handle Box ID input for retrieving details
    async def handle_get_box_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        box_id = update.message.text
        context.user_data['box_id'] = box_id

        # Retrieve box details from the database
        details = get_box_details(box_id)

        await update.message.reply_text(details, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Start the remove_box conversation
    async def start_remove_box(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.check_authorization(update):
            return ConversationHandler.END

        await update.message.reply_text("لطفاً شناسه جعبه‌ای که می‌خواهید حذف کنید وارد کنید.")
        return self.states.GET_BOX_ID

    # Handle Box ID input for removing
    async def handle_remove_box_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # Get all handlers
    def get_handlers(self):
        return [
            CommandHandler("start", self.start),
            ConversationHandler(
                entry_points=[CommandHandler("add_box", self.start_add_box)],
                states={
                    self.states.BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_box_id)],
                    self.states.SHOP_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_shop_category)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            ConversationHandler(
                entry_points=[CommandHandler("update_box_category", self.start_update_box_category)],
                states={
                    self.states.UPDATE_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_update_box_id)],
                    self.states.NEW_SHOP_CATEGORY: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_new_shop_category)
                    ],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            ConversationHandler(
                entry_points=[CommandHandler("get_box_details", self.start_get_box_details)],
                states={
                    self.states.GET_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_get_box_id)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            ConversationHandler(
                entry_points=[CommandHandler("remove_box", self.start_remove_box)],
                states={
                    self.states.GET_BOX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_remove_box_id)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
        ]