from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import create_start_link
from aiogram.filters import Command, CommandStart
from aiogram.exceptions import TelegramBadRequest
from database.database import *
import asyncio
import random

router_admin_panel = Router()

input_doctor = True
input_all_capone = True
input_peaceful_resident = True


@router_admin_panel.message(Command("admin_panel"))
async def start_cmd(message: Message, bot: Bot):
    if message.chat.type == "private":
        await message.answer("Введіть id чату в якому ви є адміністратором (Відпрате його числом аби дізнатися введіть у чаті /id і натисніть на текст)")
    else:
        await message.answer("Цю команду можна використовувати тільки у приватному чаті із <a href='https://t.me/Mafia_All_Capone_bot'>ботом</a>")

