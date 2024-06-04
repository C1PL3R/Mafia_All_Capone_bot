import asyncio, random
from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from database.database import cursor, conn

router_play = Router()

all_capone_id = 0
civilian_ids = []
doctor_id = 0

membersList = []
membersNames = []
gameTime = 0
messageOfRegistration = None

async def startGame(message: Message, bot: Bot):
    global all_capone_id, civilian_ids, doctor_id
    cursor.execute(f"SELECT creator_id FROM admin_panel WHERE group_id = %s", (message.chat.id,))
    creator_id = cursor.fetchone()[0]

    if creator_id is not None:
        cursor.execute(f"SELECT doctor FROM admin_panel WHERE creator_id = %s, group_id = %s", (creator_id, message.chat.id))
        name_of_doctor = cursor.fetchone()[0]

        cursor.execute(f"SELECT doctor_text FROM admin_panel WHERE creator_id = %s, group_id = %s", (creator_id, message.chat.id))
        description_of_doctor = cursor.fetchone()[0]

        cursor.execute(f"SELECT all_capone FROM admin_panel WHERE creator_id = %s, group_id = %s", (creator_id, message.chat.id))
        name_of_all_capone = cursor.fetchone()[0]

        cursor.execute(f"SELECT all_capone_text FROM admin_panel WHERE creator_id = %s, group_id = %s", (message.from_user.id, message.chat.id))
        description_of_all_capone = cursor.fetchone()[0]

        cursor.execute(f"SELECT civilian FROM admin_panel WHERE creator_id = %s, group_id = %s", (message.from_user.id, message.chat.id))
        name_of_civilian = cursor.fetchone()[0]

        cursor.execute(f"SELECT civilian_text FROM admin_panel WHERE creator_id = %s, group_id = %s", (message.from_user.id, message.chat.id))
        description_of_civilian = cursor.fetchone()[0]

        for id in membersList:
            roles = [name_of_doctor, name_of_all_capone, name_of_civilian]
            randomRole = random.choice(roles)
            cursor.execute("UPDATE users SET role = %s WHERE id = %s", (randomRole, id))
            conn.commit()
            if randomRole != name_of_civilian:
                roles.remove(randomRole)

            cursor.execute("SELECT role FROM users WHERE id = %s", (id,))
            role = cursor.fetchone()[0]

            if role == name_of_all_capone:
                await all_capone(message, bot)
                await bot.send_message(chat_id=id, text=description_of_all_capone)
                all_capone_id = id
            elif role == name_of_civilian:
                await civilian(message, bot)
                await bot.send_message(chat_id=id, text=description_of_civilian)
                civilian_ids.append(id)
            elif role == name_of_doctor:
                await doctor(message, bot)
                await bot.send_message(chat_id=id, text=description_of_doctor)
                doctor_id = id
    else:
        await message.answer("Власник групи не зараєстрований як власник цієї групи, щоб зареєструватися як власник цієї групи надішли мені в приват команду /construct_event")

async def all_capone(message: Message, bot: Bot):
    global all_capone_id, membersList

    list_of_victim = InlineKeyboardBuilder()

    for id in membersList:
        if id != all_capone_id:
            cursor.execute(f"SELECT name FROM users WHERE id = %s", (id,))
            member_name = cursor.fetchone()[0]

            list_of_victim.button(text=member_name, callback_data=f"{member_name}_killed")
            list_of_victim.adjust(1)

    await bot.send_message(chat_id=all_capone_id, text="Обери кого тої ночі не стане", reply_markup=list_of_victim.as_markup())

    




async def civilian(message: Message, bot: Bot):
    pass

async def doctor(message: Message, bot: Bot):
    pass


@router_play.message(Command("play"))
async def start_cmd(message: Message, bot: Bot):
    if message.chat.type in ["supergroup", "group"]:
        global membersList, membersNames, gameTime, messageOfRegistration

        link = await create_start_link(bot, f'{message.chat.id}', encode=False)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
        ])

        messageOfRegistration = await message.answer("Набір до гри!", reply_markup=keyboard, parse_mode="html")
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=messageOfRegistration.message_id)

        timerMessage = None

        MEMBERS_NUMBER = 2

        while True:
            await asyncio.sleep(1)
            gameTime += 10
            if gameTime == 180:
                if len(membersList) < MEMBERS_NUMBER:
                    await message.answer(text="<b>Таймер зупиняється! Гра закінчена</b>", parse_mode="html")

                    await timerMessage.delete()
                    await messageOfRegistration.delete()

                    break
                else:

                    await message.answer(text="<b>Гра починається!</b>", parse_mode="html")

                    await messageOfRegistration.delete()
                    await startGame(message, bot)

                    break
            if gameTime == 30:
                timerMessage30 = await messageOfRegistration.reply(text="Пройшло 30 секунд")
            elif gameTime == 60:
                timerMessage60 = await messageOfRegistration.reply(text="Пройшла 1 хвилина")
            elif gameTime == 90:
                timerMessage90 = await messageOfRegistration.reply(text="Пройшла 1 хвилина і 30 секунд")
            elif gameTime == 120:
                timerMessage120 = await messageOfRegistration.reply(text="Пройшло 2 хвилини")
            elif gameTime == 150:
                timerMessage150 = await messageOfRegistration.reply(text="Пройшло 2 хвилини і 30 секунд")
            elif gameTime == 170:
                timerMessage170 = await messageOfRegistration.reply(text="Ще 10 секунд і починаємо!")

                messages = [timerMessage30, timerMessage60, timerMessage90, timerMessage120, timerMessage150, timerMessage170]
                for mess in messages:
                    await mess.delete()
            
            if gameTime % 20 == 0:
                await messageOfRegistration.edit_text(
                    text=f"Набір до гри!\nГравці:\n<b>{', '.join(membersNames)}</b>\n\nКількість гравців: {len(membersList)}\n\nЧас: {gameTime}с.\n\nНабір до гри триває 3 хвилини.", reply_markup=keyboard, parse_mode="html")


@router_play.message(CommandStart(deep_link=True))
async def start_cmd_link(message: Message, bot: Bot):
    global membersList, membersNames, gameTime, messageOfRegistration
    if message.from_user.id in membersList:
        await message.answer(text="Ти вже приєднався!")
    elif len(membersList) >= 4:
        await message.answer("Учасників може бути тільки 4!")
    else:
        await message.answer("Ти приєднався до гри!")
        membersList.append(message.from_user.id)
        membersNames.append(message.from_user.mention_html())
        
        link = await create_start_link(bot, f'{message.chat.id}', encode=False)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
        ])

        await messageOfRegistration.edit_text(text=f"Набір до гри!\nГравці:\n<b>{', '.join(membersNames)}</b>\n\nКількість гравців: {len(membersList)}\n\nЧас: {gameTime}с.\n\nНабір до гри триває 3 хвилини.", reply_markup=keyboard, parse_mode="html")


@router_play.message(Command("leave_game"))
async def stop_game_cmd(message: Message, bot: Bot):
    global membersList, membersNames

    if message.from_user.id in membersList:
        membersList.remove(message.from_user.id)
        membersNames.remove(message.from_user.mention_html())
        await message.answer("Ти покинув гру!")
    else:
        await message.answer("Ти не був у грі!")
