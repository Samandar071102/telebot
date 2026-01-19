from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def groups_keyboard(groups):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(g[1], callback_data=f"group_{g[0]}")] for g in groups]
    )

def lesson_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"{i}-dars", callback_data=f"lesson_{i}")] for i in (1,2,3)]
    )
