from telegram import Update
from telegram.ext import ContextTypes

class AdminHandler:
    def __init__(self, mobile_models, admin_user_ids):
        self.mobile_models = mobile_models
        self.admin_user_ids = admin_user_ids

    async def admin_add_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle adding a mobile model (admin only)."""
        user_id = update.message.from_user.id
        if user_id not in self.admin_user_ids:
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
            self.mobile_models[model] = price
            await update.message.reply_text(f"✅ مدل {model} به همراه قیمت ${price} اضافه شد.")
        except ValueError:
            await update.message.reply_text("❌ فرمت اشتباه است. لطفاً از فرمت صحیح استفاده کنید: /admin_add_phone <مدل, قیمت>")

    async def admin_edit_phone_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing the price of a mobile model (admin only)."""
        user_id = update.message.from_user.id
        if user_id not in self.admin_user_ids:
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
            if model in self.mobile_models:
                self.mobile_models[model] = new_price
                await update.message.reply_text(f"✅ قیمت مدل {model} به ${new_price} تغییر یافت.")
            else:
                await update.message.reply_text("❌ مدل مورد نظر یافت نشد.")
        except ValueError:
            await update.message.reply_text("❌ فرمت اشتباه است. لطفاً از فرمت صحیح استفاده کنید: /admin_edit_phone_price <مدل, قیمت>")

    async def admin_remove_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle removing a mobile model (admin only)."""
        user_id = update.message.from_user.id
        if user_id not in self.admin_user_ids:
            await update.message.reply_text("❌ شما دسترسی به این بخش ندارید.")
            return

        command = update.message.text.strip().split(" ", 1)
        if len(command) < 2:
            await update.message.reply_text("❌ دستور نامعتبر است. لطفاً دستور صحیح را وارد کنید.")
            return

        model = command[1]
        if model in self.mobile_models:
            del self.mobile_models[model]
            await update.message.reply_text(f"✅ مدل {model} حذف شد.")
        else:
            await update.message.reply_text("❌ مدل مورد نظر یافت نشد.")