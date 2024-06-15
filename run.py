from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand
import asyncio
from logging import INFO, basicConfig

from commands.start import router_start
from commands.buy import router_pay
from commands.play import PlayCommand
from commands.construct_event import router_construct_event
from database.database import *
from config_bot import TOKEN

play_command = PlayCommand()


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher()

        self.dp.include_routers(play_command.router_play, router_start, router_construct_event)
        self.command_list = [
            BotCommand(command="start", description="Запуск бота 🤖"),
            BotCommand(command="play", description="Почати гру 🎮"),
            BotCommand(command="buy", description="Купити Підписку"),
            BotCommand(command="leave_game", description="Покинути гру"),
            BotCommand(command="construct_event", description="Конструктор івентів")
        ]    
    
    async def run(self):
        await self.bot.set_my_commands(self.command_list)
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    basicConfig(level=INFO)
    bot = TelegramBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Close connection!")
