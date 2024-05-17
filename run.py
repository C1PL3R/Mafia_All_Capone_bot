from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand
import asyncio
from logging import INFO, basicConfig

from commands.start import router_start
from commands.game import router_game
from commands.buy import router_pay
from commands.construct_event import router_construct_event
from database.database import *
from config_bot import TOKEN




async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    dp.include_routers(router_game, router_start, router_pay, router_construct_event)
    basicConfig(level=INFO)

    command_list = [(BotCommand(command="start", description="Запуск бота 🤖")),
            (BotCommand(command="game", description="Почати гру 🎮")),
            (BotCommand(command="buy", description="Купити Підписку")),
            (BotCommand(command="leave_game", description="Покинути гру"))]    
    await bot.set_my_commands(command_list)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Close connection!")
        