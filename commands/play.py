import asyncio, random
from aiogram import Bot, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, FSInputFile
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.database import cursor, conn
from .start import add_user_to_db



class PlayCommand:
    def __init__(self):
        self.router_play = Router()

        self.router_play.message.register(self.start_cmd, Command("play"))
        self.router_play.message.register(self.start_cmd_link, CommandStart(deep_link=True))
        self.router_play.message.register(self.leave_game_cmd, Command("leave_game"))

        self.router_play.callback_query.register(self.yes_btn, F.data == "answer_1")
        self.router_play.callback_query.register(self.no_btn, F.data == "answer_2")

        self.all_capone_id = 0
        self.civilian_ids = []
        self.doctor_id = 0

        self.membersList = []
        self.membersNames = []
        self.gameTime = 0
        self.messageOfRegistration = None

        self.numbers_of_members = 3

        self.list_of_victim = []


    async def night_function(self, message: Message, bot: Bot):
        gif_path = "C:/Users/Hom/Desktop/Mafia_All_Capone_bot/Media/night.gif"
        with open(gif_path, 'rb'):
            await message.answer_animation(animation=FSInputFile(path=gif_path, filename="night.gif"),
                                        caption=f"🌃Ніч 1\n\nПід покровом ночі за рогом почулися постріли і виє сирена швидкої. Сержант наказав усім тісно зачинити двері. Залишаємось на сторожі. Що ж нам може принести цей світанок....")

        cursor.execute(f"SELECT creator_id FROM admin_panel WHERE group_id = %s", (message.chat.id,))
        creator_id = cursor.fetchone()

        if creator_id is not None:
            cursor.execute("SELECT doctor, doctor_text, all_capone, all_capone_text, civilian, civilian_text FROM admin_panel WHERE creator_id = %s AND group_id = %s", (creator_id, message.chat.id))

            result = cursor.fetchone()
            if result:
                self.name_of_doctor = result[0]
                self.description_of_doctor = result[1]
                self.name_of_all_capone = result[2]
                self.description_of_all_capone = result[3]
                self.name_of_civilian = result[4]
                self.description_of_civilian = result[5]
            else:
                self.name_of_doctor = self.description_of_doctor = self.name_of_all_capone = self.description_of_all_capone = self.name_of_civilian = self.description_of_civilian = None


            for id in self.membersList:
                # if id == 1240754158:
                #     cursor.execute("UPDATE users SET role = %s WHERE id = %s", (self.name_of_civilian, id))
                #     conn.commit()
                # elif id == 5588913711:
                #     cursor.execute("UPDATE users SET role = %s WHERE id = %s", (self.name_of_doctor, id))
                #     conn.commit()
                # else:
                #     roles = [self.name_of_doctor, self.name_of_civilian]
                #     randomRole = random.choice(roles)

                #     cursor.execute("UPDATE users SET role = %s WHERE id = %s", (randomRole, id))
                #     conn.commit()

                #     if randomRole != self.name_of_civilian:
                #         roles.remove(randomRole)

                roles = [self.name_of_doctor, self.name_of_civilian, self.name_of_all_capone]
                randomRole = random.choice(roles)

                cursor.execute("UPDATE users SET role = %s WHERE id = %s", (randomRole, id))
                conn.commit()

                if randomRole != self.name_of_civilian:
                    roles.remove(randomRole)

                cursor.execute("SELECT role FROM users WHERE id = %s", (id,))
                role = cursor.fetchone()[0]

                if role == self.name_of_all_capone:
                    self.all_capone_id = int(id)
                    await bot.send_message(chat_id=self.all_capone_id, text=self.description_of_all_capone)
                    await self.all_capone(message, bot)
                    
                elif role == self.name_of_civilian:
                    await bot.send_message(chat_id=id, text=self.description_of_civilian)
                    self.civilian_ids.append(id)
                    await self.civilian(message, bot)
                    
                elif role == self.name_of_doctor:
                    await bot.send_message(chat_id=id, text=self.description_of_doctor)
                    self.doctor_id = id
                    await self.doctor(message, bot)
        else:
            await message.answer("Власник групи не зараєстрований як власник цієї групи, щоб зареєструватися як власник цієї групи надішли мені в приват команду /construct_event")


    async def startGame(self, message: Message, bot: Bot):
        await self.night_function(message=message, bot=bot)


    async def all_capone(self, message: Message, bot: Bot):
        list_of_victim_buttons = InlineKeyboardBuilder()

        for id in self.membersList:
            if id != self.all_capone_id:
                cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
                member_name = cursor.fetchone()[0]

                list_of_victim_buttons.button(text=member_name, callback_data=f"{id}_killed")
                list_of_victim_buttons.adjust(1)

                self.list_of_victim.append(id)

        await bot.send_message(chat_id=self.all_capone_id, text="Обери кого тої ночі не стане", reply_markup=list_of_victim_buttons.as_markup())

        for id in self.list_of_victim:
            self.router_play.callback_query.register(chosen_victim_def, F.data == f"{id}_killed")

            async def chosen_victim_def(self, callback: CallbackQuery):
                pass


    async def civilian(self, message: Message, bot: Bot):
        for id in self.civilian_ids:
            self.list = [("Чи любиш ти пити каву зранку?", "Так", "Ні"), ("Чи вмієш ти готувати яєчню?", "Так", "Ні"), ("Ти віддаєш перевагу перегляду фільмів вдома, чи кінотеатрі?", "Вдома", "В кінотеатрі"),
                ("Ти полюбляєш вечірні прогулянки?", "Так", "Ні"), ("Ти за паперові чи електронні книги?", "Паперові", "Електронні"), ("Ти слухаєш подкасти?", "Так", "Ні"), ("Ти маєш улюблену музичну групу, чи виконавців?", "Так", "Ні"),
                ("Чи часто ти відвідуєш музеї/виставки?", "Так", "Ні"), ("У тебе є домашні улюбленці?", "Так", "Ні"), ("Любиш подорожі на велосипеді?", "Так", "Ні")]
            
            self.list_question = random.choice(self.list)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=self.list_question[1], callback_data="answer_1"), InlineKeyboardButton(text=self.list_question[2], callback_data="answer_2")]
            ])
        
            self.mess = await bot.send_message(chat_id=id, text=f"{self.list_question[0]}", reply_markup=keyboard)


    async def doctor(self, message: Message, bot: Bot):
        list_of_patient = InlineKeyboardBuilder()

        for id in self.membersList:
            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
            member_name = cursor.fetchone()[0]

            list_of_patient.button(text=member_name, callback_data=f"{member_name}_killed")
            list_of_patient.adjust(1)

        await bot.send_message(chat_id=self.doctor_id, text="Обери кого ти спасеш", reply_markup=list_of_patient.as_markup())


    async def yes_btn(self, callback: CallbackQuery):
        await self.mess.edit_text(text=f"{self.list_question[0]}\nТи обрав: {self.list_question[1]}")


    async def no_btn(self, callback: CallbackQuery):
        await self.mess.edit_text(text=f"{self.list_question[0]}\nТи обрав: {self.list_question[2]}")
        

    async def start_cmd(self, message: Message, bot: Bot):
        if message.chat.type in ["supergroup", "group"]:
            link = await create_start_link(bot, f'{message.chat.id}', encode=False)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
            ])

            self.messageOfRegistration = await message.answer("Набір до гри!", reply_markup=keyboard, parse_mode="html")
            await bot.pin_chat_message(chat_id=message.chat.id, message_id=self.messageOfRegistration.message_id)

            timerMessage = None

            while True:
                await asyncio.sleep(1)
                self.gameTime += 1
                if self.gameTime == 120:
                    if len(self.membersList) < self.numbers_of_members:
                        await message.answer(text="<b>Таймер зупиняється! Гра закінчена</b>", parse_mode="html")

                        await timerMessage.delete()
                        await self.messageOfRegistration.delete()

                        break
                    else:

                        await message.answer(text="<b>Гра починається!</b>", parse_mode="html")

                        await self.messageOfRegistration.delete()
                        await self.startGame(message, bot)

                        self.gameTime = 0

                        break
                if self.gameTime == 30:
                    timerMessage30 = await self.messageOfRegistration.reply(text="Пройшло 30 секунд")
                elif self.gameTime == 60:
                    timerMessage60 = await self.messageOfRegistration.reply(text="Пройшла 1 хвилина")
                elif self.gameTime == 90:
                    timerMessage90 = await self.messageOfRegistration.reply(text="Пройшла 1 хвилина і 30 секунд")
                elif self.gameTime == 120:
                    timerMessage120 = await self.messageOfRegistration.reply(text="Пройшло 2 хвилини")
                elif self.gameTime == 150:
                    timerMessage150 = await self.messageOfRegistration.reply(text="Пройшло 2 хвилини і 30 секунд")
                elif self.gameTime == 170:
                    timerMessage170 = await self.messageOfRegistration.reply(text="Ще 10 секунд і починаємо!")

                    messages = [timerMessage30, timerMessage60, timerMessage90, timerMessage120, timerMessage150, timerMessage170]
                    for mess in messages:
                        await mess.delete()
        

    async def start_cmd_link(self, message: Message, bot: Bot):
        if message.from_user.id in self.membersList:
            await message.answer(text="Ти вже приєднався!")
        elif len(self.membersList) >= self.numbers_of_members:
            await message.answer("Учасників може бути тільки 4!")
        else:
            await message.answer("Ти приєднався до гри!")
            self.membersList.append(message.from_user.id)
            self.membersNames.append(message.from_user.mention_html())

            await add_user_to_db(message=message)
            
            link = await create_start_link(bot, f'{message.chat.id}', encode=False)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
            ])

            await self.messageOfRegistration.edit_text(text=f"Набір до гри!\nГравці:\n<b>{', '.join(self.membersNames)}</b>\n\nКількість гравців: {len(self.membersList)}\n\nЧас: {self.gameTime}с.\n\nНабір до гри триває 3 хвилини.", reply_markup=keyboard, parse_mode="html")


    async def leave_game_cmd(self, message: Message, bot: Bot):
        if message.from_user.id in self.membersList:
            self.membersList.remove(message.from_user.id)
            self.membersNames.remove(message.from_user.mention_html())
            await message.answer("Ти покинув гру!")
        else:
            await message.answer("Ти не був у грі!")
