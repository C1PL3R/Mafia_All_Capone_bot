from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from database.database import *

router_start = Router()

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Додати бота до групи", url='https://t.me/Mafia_All_Capone_bot?startgroup=true')]
])


async def add_user_to_db(message: Message):
    username = message.from_user.username
    telegram_id = message.from_user.id
    user_full_telegram = message.from_user.full_name
    cursor.execute("SELECT * FROM users WHERE id = %s", (telegram_id,))
    record = cursor.fetchone()

    if message.chat.type == "private" or message.chat.type == "supergroup" or message.chat.type == "group":
        if record is None:
                cursor.execute("INSERT INTO users (id, tg_name, link) VALUES (%s, %s, %s)", (telegram_id, user_full_telegram, username))
                conn.commit()
        else:
            if record[1] != user_full_telegram or record[1] != username:
                cursor.execute("UPDATE users SET tg_name = %s, link = %s WHERE id = %s", (user_full_telegram, username, telegram_id,))
                conn.commit()

@router_start.message(CommandStart())
async def start_cmd(message: Message):
    await add_user_to_db(message=message)
    await message.answer("Вітаю в боті чату: 🏴Галицький All Capone//Mafia🏴\nДля гри у групах треба такі права адміністратора:\n• Видалення повідомлення\n• Прикріплення повідомлення", reply_markup=keyboard)

