from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers import (
    start,
    cancel,
    start_add_box,
    handle_box_id,
    handle_shop_category,
    start_update_box_category,
    handle_update_box_id,
    handle_new_shop_category,
    start_get_box_details,
    handle_get_box_id,
    start_remove_box,
    handle_remove_box_id,
)
import config  # Import config for token

def main():
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Conversation handler for adding a box
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_box", start_add_box)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_box_id)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_shop_category)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Conversation handler for updating box category
    update_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("update_box_category", start_update_box_category)],
        states={
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update_box_id)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_shop_category)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Conversation handler for getting box details
    get_box_details_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get_box_details", start_get_box_details)],
        states={
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_get_box_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Conversation handler for removing a box
    remove_box_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("remove_box", start_remove_box)],
        states={
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_remove_box_id)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(update_conv_handler)
    application.add_handler(get_box_details_conv_handler)
    application.add_handler(remove_box_conv_handler)
    
    # Run the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
