from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from datetime import datetime
from db import connect
from config import ADMIN_PASSWORD

# tekshiruvchi
def is_admin(db, telegram_id: int) -> bool:
    res = db.execute("SELECT 1 FROM admins WHERE telegram_id=?", (telegram_id,)).fetchone()
    return res is not None

# parol bilan admin
async def admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin parolni kiriting:")

async def admin_password_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Parol noto‘g‘ri")
        return
    db = connect()
    db.execute("INSERT OR IGNORE INTO admins (telegram_id) VALUES (?)",
               (update.message.from_user.id,))
    db.commit()
    db.close()
    await update.message.reply_text("✅ Admin huquqi berildi")

# darsni boshlash
async def start_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = connect()
    if not is_admin(db, update.message.from_user.id):
        db.close()
        await update.message.reply_text("❌ Siz admin emassiz")
        return

    groups = db.execute("SELECT id, name FROM groups").fetchall()
    db.close()

    kb = [[InlineKeyboardButton(g[1], callback_data=f"grp_{g[0]}")] for g in groups]

    await update.message.reply_text(
        "📘 Guruhni tanlang:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# dars raqamini tanlash
async def choose_lesson_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    group_id = int(query.data.split("_")[1])

    kb = [[InlineKeyboardButton(f"{i}-dars", callback_data=f"lesson_{group_id}_{i}")] for i in (1,2,3)]

    await query.message.reply_text(
        "📚 Dars raqamini tanlang:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# o‘quvchilar ro‘yxati + attendance tugmalari
async def open_attendance_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, group_id, lesson_no = query.data.split("_")
    group_id, lesson_no = int(group_id), int(lesson_no)

    db = connect()
    cur = db.cursor()

    # dars yaratish
    cur.execute("INSERT INTO lessons (group_id,date,lesson_number,started_at) VALUES (?,?,?,?)",
                (group_id, datetime.now().date().isoformat(), lesson_no, datetime.now().strftime("%H:%M:%S")))
    lesson_id = cur.lastrowid

    students = cur.execute(
        "SELECT s.id, s.first_name, s.last_name, p.telegram_id FROM students s JOIN parents p ON s.parent_id=p.id WHERE s.group_id=?",
        (group_id,)
    ).fetchall()

    db.commit()
    db.close()

    context.user_data["lesson_id"] = lesson_id

    for s in students:
        student_id, fname, lname, parent_tid = s
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Keldi", callback_data=f"att_{student_id}_present_{parent_tid}"),
             InlineKeyboardButton("⏰ Kech", callback_data=f"att_{student_id}_late_{parent_tid}"),
             InlineKeyboardButton("❌ Kelmadi", callback_data=f"att_{student_id}_absent_{parent_tid}")]
        ])
        await query.message.reply_text(f"👤 {fname} {lname}", reply_markup=kb)

# attendance belgilash + ota-onaga xabar
async def mark_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, student_id, status, parent_tid = query.data.split("_")
    student_id, parent_tid = int(student_id), int(parent_tid)
    lesson_id = context.user_data.get("lesson_id")
    now = datetime.now().strftime("%H:%M:%S")

    db = connect()
    cur = db.cursor()

    # bir martalik tekshiruv
    exists = cur.execute("SELECT 1 FROM attendance WHERE lesson_id=? AND student_id=?",
                         (lesson_id, student_id)).fetchone()
    if exists:
        db.close()
        await query.message.reply_text("⚠️ Bu o‘quvchi allaqachon belgilangan")
        return

    cur.execute("INSERT INTO attendance (lesson_id, student_id, status, check_in_time) VALUES (?,?,?,?)",
                (lesson_id, student_id, status, now))
    db.commit()
    db.close()

    # ota-onaga xabar
    text = f"📚 Dars haqida ma’lumot\n👤 Farzandingiz: {status.upper()}\n⏰ Vaqt: {now}"
    await context.bot.send_message(chat_id=parent_tid, text=text)

    await query.message.edit_reply_markup(reply_markup=None)
