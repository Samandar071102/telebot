from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from config import BOT_TOKEN
from db import init_db
from parent_handlers import *
from admin_handlers import *
from states import *

init_db()

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ota-ona
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start_parent)],
        states={
            ADD_FIRST: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_first)],
            ADD_LAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_last)],
            ADD_GROUP: [CallbackQueryHandler(add_group)]
        },
        fallbacks=[]
    ))

    # admin
    app.add_handler(CommandHandler("admin", admin_login))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_password_check))

    app.add_handler(CommandHandler("start_lesson", start_lesson))

    app.run_polling()

if __name__ == "__main__":
    main()
