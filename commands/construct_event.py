from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.database import *

router_construct_event = Router()

@router_construct_event.message(Command("construct_event"))
async def order(message: Message):
    await message.answer("<blockquote><i><u><b>Конструктора івентів ще нема(</b></u></i></blockquote>", parse_mode="html")