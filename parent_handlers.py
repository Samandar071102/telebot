from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from db import connect
from states import ADD_FIRST, ADD_LAST, ADD_GROUP
from keyboards import groups_keyboard

async def start_parent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Farzandingiz ismini kiriting:")
    return ADD_FIRST

async def add_first(update: Update, context):
    context.user_data["first"] = update.message.text
    await update.message.reply_text("Familiyani kiriting:")
    return ADD_LAST

async def add_last(update: Update, context):
    context.user_data["last"] = update.message.text
    db = connect()
    groups = db.execute("SELECT * FROM groups").fetchall()
    db.close()
    await update.message.reply_text(
        "Guruhni tanlang:",
        reply_markup=groups_keyboard(groups)
    )
    return ADD_GROUP

async def add_group(update: Update, context):
    query = update.callback_query
    await query.answer()

    group_id = int(query.data.split("_")[1])
    db = connect()
    cur = db.cursor()

    # ota-onani qo‘shish
    cur.execute(
        "INSERT OR IGNORE INTO parents (telegram_id) VALUES (?)",
        (query.from_user.id,)
    )

    parent_id = cur.execute(
        "SELECT id FROM parents WHERE telegram_id=?",
        (query.from_user.id,)
    ).fetchone()[0]

    # farzand qo‘shish
    cur.execute(
        "INSERT INTO students (first_name,last_name,group_id,parent_id) VALUES (?,?,?,?)",
        (context.user_data["first"], context.user_data["last"], group_id, parent_id)
    )

    db.commit()
    db.close()

    await query.message.reply_text("Farzandingiz muvaffaqiyatli qo‘shildi.")
    return ConversationHandler.END
