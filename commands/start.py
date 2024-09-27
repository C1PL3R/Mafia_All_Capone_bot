from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from database.database import *

router_start = Router()

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Додати бота до групи", url='https://t.me/Mafia_All_Capone_bot?startgroup=true')]
])


async def add_user_to_db(message: Message):
    username = message.from_user.username
    telegram_id = message.from_user.id
    username_telegram = message.from_user.first_name
    cursor.execute("SELECT * FROM users WHERE id = %s", (telegram_id,))
    record = cursor.fetchone()

    if message.chat.type == "private" or message.chat.type == "supergroup" or message.chat.type == "group":
        if record is None:
                cursor.execute("INSERT INTO users (id, tg_name, link) VALUES (%s, %s, %s)", (telegram_id, username_telegram, username))
                conn.commit()
        else:
            if record[1] != username_telegram or record[1] != username:
                cursor.execute("UPDATE users SET tg_name = %s, link = %s WHERE id = %s", (username_telegram, username, telegram_id,))
                conn.commit()

@router_start.message(CommandStart())
async def start_cmd(message: Message):
    await add_user_to_db(message=message)
    await message.answer("Вітаю в боті чату: 🏴Галицький All Capone//Mafia🏴\nДля гри у групах треба такі права адміністратора:\n• Видалення повідомлення\n• Прикріплення повідомлення", reply_markup=keyboard)


@router_start.message(Command("id"))
async def id_cmd(message: Message):
    if message.chat.type == "private":
        await message.answer(f"Ваше id: <code>{message.chat.id}</code>", parse_mode="html")
    if message.chat.type in ["supergroup", "group"]:
        await message.answer(f"Id вашого чату: <code>{message.chat.id}</code>", parse_mode="html")


@router_start.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer("‼️ Увага ‼️\n\nЗа будь-яку інфорацію яку надіслав бот несе відповідальність власник чату, якщо це не реклама!")

