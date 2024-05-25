import asyncio
from aiogram import Bot, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import create_start_link
from aiogram.exceptions import TelegramBadRequest

router_play = Router()

membersList = []
membersNames = []
gameTime = 0
messageReg = None

async def startGame(message: types.Message, bot: Bot):
    pass


@router_play.message(Command("play"))
async def start_cmd(message: types.Message, bot: Bot):
    if message.chat.type in ["supergroup", "group"]:
        global membersList, membersNames, gameTime, messageReg

        link = await create_start_link(bot, f'{message.chat.id}', encode=False)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
        ])

        messageReg = await message.answer("Набір до гри!", reply_markup=keyboard)
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=messageReg.message_id)

        timerMessage = None

        MEMBERS_NUMBER = 2

        while True:
            await asyncio.sleep(1)
            gameTime += 10
            if gameTime == 180:
                if len(membersList) < MEMBERS_NUMBER:
                    await message.answer(text="<b>Таймер зупиняється! Гра закінчена</b>")
                    await timerMessage.delete()
                    await messageReg.delete()
                else:
                    await message.answer(text="<b>Гра починається!</b>")
                    await startGame(message, bot)
                break
            if gameTime == 30:
                timerMessage = await messageReg.reply(text="Пройшло 30 секунд")
            elif gameTime == 60:
                await timerMessage.delete()
                timerMessage = await messageReg.reply(text="Пройшла 1 хвилина")
            elif gameTime == 90:
                await timerMessage.delete()
                timerMessage = await messageReg.reply(text="Пройшла 1 хвилина і 30 секунд")
            elif gameTime == 120:
                await timerMessage.delete()
                timerMessage = await messageReg.reply(text="Пройшло 2 хвилини")
            elif gameTime == 150:
                await timerMessage.delete()
                timerMessage = await messageReg.reply(text="Пройшло 2 хвилини і 30 секунд")
            elif gameTime == 170:
                await timerMessage.delete()
                timerMessage = await messageReg.reply(text="Ще 10 секунд і починаємо!")
            
            if gameTime % 20 == 0:
                await messageReg.edit_text(
                    text=f"Набір до гри!\nГравці:\n<b>{', '.join(membersNames)}</b>\n\nКількість гравців: {len(membersList)}\n\nЧас: {gameTime}с.\n\nНабір до гри триває 3 хвилини.", reply_markup=keyboard)


@router_play.message(CommandStart(deep_link=True))
async def start_cmd_link(message: types.Message, bot: Bot):
    global membersList, membersNames, gameTime, messageReg
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

        await messageReg.edit_text(text=f"Набір до гри!\nГравці:\n<b>{', '.join(membersNames)}</b>\n\nКількість гравців: {len(membersList)}\n\nЧас: {gameTime}с.\n\nНабір до гри триває 3 хвилини.", reply_markup=keyboard)


@router_play.message(Command("leave_game"))
async def stop_game_cmd(message: types.Message, bot: Bot):
    global membersList, membersNames

    if message.from_user.id in membersList:
        membersList.remove(message.from_user.id)
        membersNames.remove(message.from_user.mention_html())
        await message.answer("Ти покинув гру!")
    else:
        await message.answer("Ти не був у грі!")
