from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberOwner
from database.database import *

router_construct_event = Router()

isInputChatId = True
isInputCreatorId = True
CreatorId = 0
ChatId = 0

async def loggingIn(message: Message):
    global isInputChatId, isInputCreatorId, ChatId, CreatorId
    isInputCreatorId = True

    await message.answer("Ти не зареєстрований як той хто являється тим хто створив чат. Розпочнімо реєстрування. Надішли своє id (Своє id можна дізнатися надіславши у приват бота команду /id)", parse_mode="html")

    @router_construct_event.message(lambda message: isInputCreatorId)
    async def isInputCreatorIdAsyncDef(message: Message):
        if message.chat.type == "private":
            try:
                global isInputChatId, isInputCreatorId, ChatId, CreatorId
                CreatorId = int(message.text)

                await message.answer(text="Дякую ❤️\nТепер надішли айді групи яку <u><b>ти створив</b></u> адже створювати івент може <u><b>тільки людина яка створила групу</b></u> 🙂\nЩоб дізнатися id групи надішли команду /id у групу яку <u><b>ти створив</b></u>")

                isInputCreatorId = False
                isInputChatId = True

                @router_construct_event.message(lambda message: isInputChatId)
                async def isInputChatIdAsyncDef(message: Message, bot: Bot):
                    if message.chat.id == "private":
                        try:
                            YouIsCreator = False
                            global isInputChatId, ChatId, CreatorId
                            ChatId = int(message.text)
                            if ChatId > 0:
                                await message.answer("Відправ айді групи (воно з мінусом)")
                            else:
                                administrators = await bot.get_chat_administrators(ChatId)

                                isInputChatId = False

                                for admin in administrators:
                                    if isinstance(admin, ChatMemberOwner) and admin.user.id == CreatorId:
                                        YouIsCreator = True
                                        
                                if YouIsCreator:
                                    cursor.execute("UPDATE creator_id = ?, group_id = ?", (message.from_user.id,))
                                    conn.commit()
                                    await message.answer("Тепер відправ команду /construct_event ще раз!")
                                else:
                                    await message.answer("Ви не створювали цю групу.")
                                    ChatId = 0
                                    CreatorId = 0

                        except Exception:
                            await message.answer("Надішли тільки id групи яку <u><b>ти створив</b></u> без букв, самі цифри", parse_mode="html")

            except Exception:
                isInputChatId = False
                isInputCreatorId = False
                await message.answer(text="Надішли тільки своє id без букв, самі цифри")

@router_construct_event.message(Command("construct_event"))
async def order(message: Message):
    if message.chat.type == "private":
        cursor.execute("SELECT creator_id FROM admin_panel")
        creatorIds = cursor.fetchall()
        if message.from_user.id in creatorIds:
            await message.answer("Ти в базі)")
        else:
            await loggingIn(message)

        