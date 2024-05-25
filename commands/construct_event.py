from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.database import *

router_construct_event = Router()

isInputChatId = True
isInputCreatorId = True
CreatorId = 0
ChatId = 0

@router_construct_event.message(Command("construct_event"))
async def order(message: Message):
    global isInputChatId, isInputCreatorId, ChatId, CreatorId
    isInputCreatorId = True
    await message.answer("Надішли своє id (Своє id можна дізнатися надіславши у приват бота команду /id)", parse_mode="html")
    @router_construct_event.message(lambda message: isInputCreatorId)
    async def isInputCreatorIdAsyncDef(message: Message):
        try:
            global isInputChatId, isInputCreatorId, ChatId, CreatorId
            CreatorId = int(message.text)

            await message.answer(text="Дякую ❤️\nТепер надішли айді групи в яку <u><b>ти створив</b></u> адже створювати івент може <u><b>тільки людина яка створила групу</b></u> 🙂\nЩоб дізнатися id групи надішли команду")

            isInputCreatorId = False
            isInputChatId = True

            @router_construct_event.message(lambda message: isInputChatId)
            async def isInputChatIdAsyncDef(message: Message):

        except Exception:
            await message.answer(text="Надішли тільки своє id без букв самі цифри")