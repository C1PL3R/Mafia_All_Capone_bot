from aiogram import Bot, Dispatcher
from aiogram.types.bot_command import BotCommand
import asyncio
from logging import INFO, basicConfig

from commands.start import router_start
from commands.game import router_game, tg_names
from database.database import *
from config_bot import TOKEN




async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    dp.include_routers(router_game, router_start)
    basicConfig(level=INFO)

    command_list = [(BotCommand(command="start", description="Запуск бота 🤖")),
            (BotCommand(command="game", description="Почати гру 🎮"))]
    
    await bot.set_my_commands(command_list)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Close connection!")
        print(tg_names)
        local_list = [5588913711, 1240754158]
        for id in local_list:
            cursor.execute("UPDATE users SET killed = %s WHERE id = %s", (0, id,))
            conn.commit()