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


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher()
        self.play_command = PlayCommand()

        self.dp.include_routers(self.play_command.router_play, router_start, router_construct_event,router_pay )
        self.command_list = [
            BotCommand(command="start", description="Запуск бота 🤖"),
            BotCommand(command="help", description="Допомога 🆘"),
            BotCommand(command="play", description="Почати гру 🎮"),
            BotCommand(command="buy_subscription", description="Купити/Продовжити Підписку"),
            BotCommand(command="stop_subscription", description="Призупинити підписку"),
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
