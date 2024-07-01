import asyncio, random, html
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
        self.router_play.message.register(self.last_message, lambda message: self.is_last_message)

        self.chat_id = 0

        self.all_capone_id = 0
        self.civilian_ids = []
        self.doctor_id = 0

        self.membersList = []
        self.membersNames = []
        self.gameTime = 0

        self.messageOfRegistration = None
        self.choose_who_you_will_cured = None
        self.choose_who_you_will_kill = None

        self.numbers_of_members = 2

        self.list_of_victim = []
        self.list_of_patient = []
        self.list_of_candidates = []

        self.question_and_two_answers = []

        self.victim_id = 0
        self.patient_id = 0

        self.victim_text = ""

        self.is_last_message = False
        self.message_for_civilian = None
        self.is_killed = 0


    async def night_function(self, message: Message, bot: Bot):
        url_button = InlineKeyboardButton(text="Перейти до бота", url="https://t.me/Mafia_All_Capone_bot")

        self.url_buttons = InlineKeyboardMarkup(inline_keyboard=[[url_button]])

        gif_path = "C:/Users/Hom/Desktop/Mafia_All_Capone_bot/Media/night.gif"
        with open(gif_path, 'rb'):
            await message.answer_animation(animation=FSInputFile(path=gif_path, filename="night.gif"),
                                        caption=f"🌃Ніч 1\n\nПід покровом ночі за рогом почулися постріли і виє сирена швидкої. Сержант наказав усім тісно зачинити двері. Залишаємось на сторожі. Що ж нам може принести цей світанок....",
                                        reply_markup=self.url_buttons)

        cursor.execute("SELECT creator_id FROM admin_panel WHERE group_id = %s", (message.chat.id,))
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
                cursor.execute("UPDATE users SET killed = %s WHERE id = %s", (0, id,))
                conn.commit()

                cursor.execute("UPDATE users SET cured = %s WHERE id = %s", (0, id,))
                conn.commit()

                roles = [self.name_of_doctor, self.name_of_civilian, self.name_of_all_capone]
                # roles = [self.name_of_civilian]
                randomRole = random.choice(roles)
                
                cursor.execute("UPDATE users SET role = %s WHERE id = %s", (randomRole, id))
                conn.commit()

                print(randomRole)

                if randomRole in [self.name_of_all_capone, self.name_of_doctor]:
                    roles.remove(randomRole)

                cursor.execute("SELECT role FROM users WHERE id = %s", (id,))
                role = cursor.fetchone()[0]

                if role == self.name_of_all_capone:
                    self.all_capone_id = int(id)
                    await bot.send_message(chat_id=self.all_capone_id, text=self.description_of_all_capone, message_effect_id="5159385139981059251")
                    await self.all_capone(message, bot)
                    
                elif role == self.name_of_civilian:
                    await bot.send_message(chat_id=id, text=self.description_of_civilian, message_effect_id="5159385139981059251")
                    self.civilian_ids.append(id)
                    await self.civilian(message, bot)
                    
                elif role == self.name_of_doctor:
                    await bot.send_message(chat_id=id, text=self.description_of_doctor, message_effect_id="5159385139981059251")
                    self.doctor_id = id
                    await self.doctor(message, bot)
        else:
            await message.answer("Власник групи не зараєстрований як власник цієї групи, щоб зареєструватися як власник цієї групи надішли мені в приват команду /construct_event")


    async def day_function(self, message: Message, bot: Bot):
        if self.victim_id != 0 and self.patient_id != 0:
            list_of_id = [self.patient_id, self.patient_id]
        elif self.victim_id == 0:
            list_of_id = [self.patient_id]
        elif self.patient_id == 0:
            list_of_id = [self.victim_id]
        else:
            await message.answer("Увага! Помилка, перезапустіть гру!")

        for id in list_of_id:
            cursor.execute("SELECT cured FROM users WHERE id = %s", (id,))
            cured = cursor.fetchone()[0]
            cursor.execute("SELECT killed FROM users WHERE id = %s", (id,))
            killed = cursor.fetchone()[0]

            if killed == 1 and cured == 1 or cured == 1:
                cursor.execute("UPDATE users SET cured = %s WHERE id = %s", (1, id,))
                conn.commit()
                cursor.execute("UPDATE users SET killed = %s WHERE id = %s", (0, id,))
                conn.commit()
                
                await bot.send_message(chat_id=id, text="До тебе в гості прийшов лікар")

                self.is_killed = 0


            elif killed == 1 and cured == 0 or killed == 1:
                cursor.execute("UPDATE users SET cured = %s WHERE id = %s", (0, id,))
                conn.commit()
                cursor.execute("UPDATE users SET killed = %s WHERE id = %s", (1, id,))
                conn.commit()

                self.membersList.remove(id)
                for member in self.membersNames:
                        if member[0] == id:
                            self.membersNames.remove(member)
                            break                
                
                if id in self.list_of_patient:
                    self.list_of_patient.remove(id)
                
                if id in self.list_of_victim:
                    self.list_of_victim.remove(id)
                
                if id in self.civilian_ids:
                    self.civilian_ids.remove(id)

                cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (self.victim_id,))
                name = cursor.fetchone()[0]

                self.victim_text = f"{self.name_of_all_capone} {name}"

                await bot.send_message(chat_id=id, text="Тебе вбили! Напиши своє останнє повідолмення!")
                self.is_last_message = True

                self.is_killed = 1


        gif_path = "C:/Users/Hom/Desktop/Mafia_All_Capone_bot/Media/day.gif"

        with open(gif_path, 'rb'):
            await message.answer_animation(animation=FSInputFile(path=gif_path, filename="day.gif"),
                                            caption=f"🌄 День\n\nРанкова тиша порушена не ароматом кави, а...")
            
        if self.is_killed == 1:
            await message.answer(f"Жахливою трагедією. Цієї ночі безцінний {self.victim_text} був жорстоко вбитий. Сорока на хвості принесла звістку, що в нього в гостях був Аль Капоне.")
        elif self.is_killed == 0:
            message.answer("Ніч минула без жертв!")

        players_text = "\n".join([f"{i+1}. {name[1]}" for i, name in enumerate(self.membersNames)])

        await message.answer(f'Список гравців:\n{players_text}\n\nКількість гравців: {len(self.membersList)}\n\n<b>До голосування лишається 45 секунд!</b>', parse_mode="html")

        await asyncio.sleep(45)
        await self.voiting_function(message=message, bot=bot)


    async def voiting_function(self, message: Message, bot: Bot):
        list_of_cadidates_buttons = InlineKeyboardBuilder()

        for id in self.membersList:
            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
            candidate_name = cursor.fetchone()[0]

            list_of_cadidates_buttons.button(text=candidate_name, callback_data=f"{id}_candidate")
            list_of_cadidates_buttons.adjust(1)

            self.list_of_candidates.append((id, 0))
            
        for id in self.membersList:
            self.message_list_of_candidates = await bot.send_message(chat_id=id, text="Обери за кого ти проголосуєш:", reply_markup=list_of_cadidates_buttons.as_markup())

        for id, voites in self.list_of_candidates:
            self.router_play.callback_query.register(self.chosen_candidate_def(candidate_id=id), F.data == f"{id}_candidate")


    def chosen_candidate_def(self, candidate_id):
        async def handler(callback: CallbackQuery, bot: Bot):
            mess = self.message_list_of_candidates

            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (candidate_id,))
            candidate_name = cursor.fetchone()[0]

            await bot.edit_message_text(chat_id=callback.from_user.id, message_id=mess.message_id, text=f"Обери за кого ти проголосуєш:\nТи вибрав: {candidate_name}")

            cursor.execute("SELECT tg_name FROM users WHERE id = %s", (callback.from_user.id,))
            member_name = cursor.fetchone()[0]
            await bot.send_message(chat_id=self.chat_id, text=f"{member_name} проголосував за {candidate_name}")
            
            for i, (id, votes) in enumerate(self.list_of_candidates):
                if id == self.list_of_candidates[i][0]:
                    self.list_of_candidates[i][1] + 1
                    print(self.list_of_candidates[i])

        return handler


    async def startGame(self, message: Message, bot: Bot):
        self.chat_id = message.chat.id
        await self.night_function(message=message, bot=bot)


        await asyncio.sleep(60)
        await self.day_function(message=message, bot=bot)


    async def last_message(self, message: Message, bot: Bot):
        await bot.send_message(chat_id=self.victim_id, text="Очікуй на нову гру")

        await bot.send_message(chat_id=self.chat_id, text=f"Останнє повідомлення вбитого:\n\n{message.text}")
        self.is_last_message = False


    async def all_capone(self, message: Message, bot: Bot):
        list_of_victim_buttons = InlineKeyboardBuilder()

        for id in self.membersList:
            if id != self.all_capone_id:
                cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
                member_name = cursor.fetchone()[0]

                list_of_victim_buttons.button(text=member_name, callback_data=f"{id}_killed")
                list_of_victim_buttons.adjust(1)

                self.list_of_victim.append(id)

        self.choose_who_you_will_kill = await bot.send_message(chat_id=self.all_capone_id, text="Обери кого тої ночі не стане", reply_markup=list_of_victim_buttons.as_markup())

        for id in self.list_of_victim:
            self.router_play.callback_query.register(self.chosen_victim_def(id), F.data == f"{id}_killed")


    def chosen_victim_def(self, id):
        async def handler(callback: CallbackQuery, bot: Bot):
            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
            member_name = cursor.fetchone()[0]

            await bot.edit_message_text(chat_id=self.all_capone_id, 
                                        message_id=self.choose_who_you_will_kill.message_id, 
                                        text=f"Обери кого тої ночі не стане:\nТи обрав: {member_name}")

            await bot.send_message(chat_id=self.chat_id, text="Аль Капоне вибрав жертву")  

            cursor.execute("UPDATE users SET killed = %s WHERE id = %s", (1, id,))
            conn.commit()

            self.victim_id = id
            
        return handler


    async def civilian(self, message: Message, bot: Bot):
        print(self.civilian_ids)
        for id in self.civilian_ids:
            self.question_and_two_answers = [("Чи любиш ти пити каву зранку?", "Так", "Ні"), ("Чи вмієш ти готувати яєчню?", "Так", "Ні"), ("Ти віддаєш перевагу перегляду фільмів вдома, чи кінотеатрі?", "Вдома", "В кінотеатрі"),
                ("Ти полюбляєш вечірні прогулянки?", "Так", "Ні"), ("Ти за паперові чи електронні книги?", "Паперові", "Електронні"), ("Ти слухаєш подкасти?", "Так", "Ні"), ("Ти маєш улюблену музичну групу, чи виконавців?", "Так", "Ні"),
                ("Чи часто ти відвідуєш музеї/виставки?", "Так", "Ні"), ("У тебе є домашні улюбленці?", "Так", "Ні"), ("Любиш подорожі на велосипеді?", "Так", "Ні")]
            
            self.list_question = random.choice(self.question_and_two_answers)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=self.list_question[1], callback_data="answer_1"), InlineKeyboardButton(text=self.list_question[2], callback_data="answer_2")]
            ])
        
            self.message_for_civilian = await bot.send_message(chat_id=id, text=f"{self.list_question[0]}", reply_markup=keyboard)


    async def yes_btn(self, callback: CallbackQuery, bot: Bot):
        message = self.message_for_civilian
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=message.message_id, text=f"{self.list_question[0]}\nТи обрав: {self.list_question[1]}")


    async def no_btn(self, callback: CallbackQuery, bot: Bot):
        message = self.message_for_civilian
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=message.message_id, text=f"{self.list_question[0]}\nТи обрав: {self.list_question[2]}")


    async def doctor(self, message: Message, bot: Bot):
        
        list_of_patient_buttons = InlineKeyboardBuilder()

        for id in self.membersList:
            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
            member_name = cursor.fetchone()[0]

            list_of_patient_buttons.button(text=member_name, callback_data=f"{id}_cured")
            list_of_patient_buttons.adjust(1)

            self.list_of_patient.append(id)
            

        self.choose_who_you_will_cured = await bot.send_message(chat_id=self.doctor_id, text="Обери кого ти спасеш", reply_markup=list_of_patient_buttons.as_markup())

        for id in self.list_of_patient:
            self.router_play.callback_query.register(self.chosen_patient_def(id), F.data == f"{id}_cured")


    def chosen_patient_def(self, id):
        async def handler(callback: CallbackQuery, bot: Bot):
            cursor.execute(f"SELECT tg_name FROM users WHERE id = %s", (id,))
            member_name = cursor.fetchone()[0]

            await bot.edit_message_text(chat_id=self.doctor_id, 
                                        message_id=self.choose_who_you_will_cured.message_id, 
                                        text=f"Обери кого ти спасеш:\nТи обрав: {member_name}")

            await bot.send_message(chat_id=self.chat_id, text="Лікар вибрав пацієнта")

            cursor.execute("UPDATE users SET cured = %s WHERE id = %s", (1, id,))
            conn.commit()

            self.patient_id = id
        return handler
        

    async def start_cmd(self, message: Message, bot: Bot):
        if message.chat.type in ["supergroup", "group"]:
            link = await create_start_link(bot, f'{message.chat.id}', encode=False)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
            ])

            self.messageOfRegistration = await message.answer("Набір до гри!", reply_markup=keyboard, parse_mode="html")
            await bot.pin_chat_message(chat_id=message.chat.id, message_id=self.messageOfRegistration.message_id)

            while True:
                await asyncio.sleep(1)
                self.gameTime += 10
                if self.gameTime == 120:
                    if len(self.membersList) < self.numbers_of_members:
                        await message.answer(text="<b>Таймер зупиняється! Гра закінчена</b>", parse_mode="html")

                        await self.messageOfRegistration.delete()

                        break
                    else:

                        await message.answer(text="<b>Гра починається!</b>", parse_mode="html")

                        await self.messageOfRegistration.delete()
                        await self.startGame(message=message, bot=bot)

                        self.gameTime = 0

                        break
                if self.gameTime == 30:
                    timerMessage30 = await self.messageOfRegistration.reply(text="Пройшло 30 секунд")
                elif self.gameTime == 60:
                    timerMessage60 = await self.messageOfRegistration.reply(text="Пройшла 1 хвилина")
                elif self.gameTime == 90:
                    timerMessage90 = await self.messageOfRegistration.reply(text="Пройшла 1 хвилина і 30 секунд")

                    messages = [timerMessage30, timerMessage60, timerMessage90]
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

            await add_user_to_db(message=message)
            
            link = await create_start_link(bot, f'{message.chat.id}', encode=False)

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Приєднатися до гри!", url=link)]
            ])

            name = f'<a href="tg://user?id={message.from_user.id}">{html.escape(message.from_user.first_name)}</a>'
            self.membersNames.append((message.from_user.id, name))

            members_names = ', '.join([name for _, name in self.membersNames])

            await self.messageOfRegistration.edit_text(
                text=f"Набір до гри!\nГравці:\n<b>{members_names}</b>\n\nКількість гравців: {len(self.membersNames)}\n\nЧас: {self.gameTime}с.\n\nНабір до гри триває 3 хвилини.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )


    async def leave_game_cmd(self, message: Message, bot: Bot):
        if message.from_user.id in self.membersList:
            self.membersList.remove(message.from_user.id)
            self.membersNames.remove(message.from_user.mention_html())
            await message.answer("Ти покинув гру!")
        else:
            await message.answer("Ти не був у грі!")
