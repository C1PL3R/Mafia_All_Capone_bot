import asyncio
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, ChatMemberOwner, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from database.database import cursor, conn

router_construct_event = Router()

is_input_chat_id = False
is_input_add_chat_id = False
is_input_creator_id = False
is_input_name_of_role = False
is_input_description_of_role = False
creator_id = 0
chat_id = 0
name_of_chats = []
name_of_add_chats = []
group_id = 0

@router_construct_event.message(Command("construct_event"))
async def construct_event_handler(message: Message, bot: Bot):
    global name_of_chats
    if message.chat.type == "private":
        cursor.execute("SELECT creator_id FROM admin_panel")
        creator_ids = [row[0] for row in cursor.fetchall()]

        if message.from_user.id in creator_ids:
            cursor.execute("SELECT group_id FROM admin_panel WHERE creator_id = %s", (message.from_user.id,))
            group_ids = cursor.fetchall()

            list_of_chats = InlineKeyboardBuilder()

            for chat_id in group_ids:
                chat = await bot.get_chat(chat_id=int(chat_id[0]))

                list_of_chats.button(text=f"{chat.title}", callback_data=chat.title)

                name_of_chats.append((chat_id, chat.title))
                
                list_of_chats.adjust(1)

            await message.answer("Вибери чат де будеш будувати івент", reply_markup=list_of_chats.as_markup())

        else:
            global is_input_chat_id

            await message.answer("Ти не зареєстрований як власник чату. Розпочнімо реєстрування.\nНадішли айді групи яку <u><b>ти створив</b></u> адже створювати івент може <u><b>тільки людина яка створила групу</b></u> 🙂\nЩоб дізнатися id групи надішли команду /id у групу яку <u><b>ти створив</b></u>", parse_mode="html")
            
            is_input_chat_id = True
        
        for id, title in name_of_chats:
            @router_construct_event.callback_query(F.data == title)
            async def titleChatCallback(callback: CallbackQuery):
                global group_id
                doctor_button = InlineKeyboardButton(text="Лікар", callback_data="doctor")
                all_capone_button = InlineKeyboardButton(text="Аль Капоне", callback_data="all_capone")
                civilian_button = InlineKeyboardButton(text="Мирний житель", callback_data="civilian")
                add_group_button = InlineKeyboardButton(text="➕ Додати групу ➕", callback_data="add_group")
                delete_group_button = InlineKeyboardButton(text="❌ Видалити групу ❌", callback_data="delete_group")
                default_settings_button = InlineKeyboardButton(text="Скинути все!", callback_data="default")

                roles_buttons = InlineKeyboardMarkup(inline_keyboard=[
                    [doctor_button],
                    [all_capone_button],
                    [civilian_button],
                    [add_group_button],
                    [delete_group_button],
                    [default_settings_button]
                ])
                group_id = id
                await callback.message.edit_text("⬇️ Вибери яку роль ти хочеш змінити ⬇️", reply_markup=roles_buttons)


@router_construct_event.message(lambda message: is_input_chat_id)
async def is_input_chat_id_handler(message: Message, bot: Bot):
    if message.chat.type == "private":
        try:
            try:
                global is_input_chat_id, chat_id, creator_id
                chat_id = int(message.text)

                if chat_id >= 0:
                    await message.answer("Відправ айді групи (воно завжди з мінусом)")
                elif chat_id < 0:
                    chat_member = await bot.get_chat_member(chat_id, message.from_user.id)

                    status = chat_member.status

                    if status == ChatMemberStatus.CREATOR:
                        cursor.execute("INSERT INTO admin_panel (creator_id, group_id) VALUES (%s, %s)", (message.from_user.id, chat_id))
                        conn.commit()

                        chat = await bot.get_chat(chat_id=chat_id)

                        await message.answer(f"Ти зареєстрований як власник групи: <u><b>{chat.title}</b></u>\nТепер відправ команду /construct_event ще раз!", parse_mode="html")
                        is_input_chat_id = False
                    else:
                        await message.answer("Ти не є власником цієї групи.")
                        chat_id = 0
                        creator_id = 0
                        is_input_chat_id = False

            except TelegramBadRequest as e:
                await message.answer(f"Такої групи не існує!\n<b>{e}</b>", parse_mode="html")
        except ValueError:
            await message.answer("Надішли тільки id групи яку <u><b>ти створив</b></u> без букв, самі цифри", parse_mode="html")


async def change_name_of_role(callback: CallbackQuery, name_of_role, role_in_db, chat_id):
    cursor.execute(f"SELECT {role_in_db} FROM admin_panel WHERE creator_id = %s AND group_id = %s", (callback.from_user.id, chat_id))
    role = cursor.fetchone()

    cursor.execute(f"SELECT {role_in_db}_text FROM admin_panel WHERE creator_id = %s AND group_id = %s", (callback.from_user.id, chat_id))
    text_of_role = cursor.fetchone()

    go_to_main_menu_button = InlineKeyboardButton(text="⬅️ Назад ⬅️", callback_data="go_to_main_menu")
    name_of_role_button = InlineKeyboardButton(text="Назву ролі", callback_data="name_of_role")
    description_of_role_button = InlineKeyboardButton(text="Опис ролі", callback_data="description_of_role")

    control_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [name_of_role_button],
        [description_of_role_button],
        [go_to_main_menu_button]
    ])

    await callback.message.edit_text(text=f"Поточна назва ролі «{name_of_role}»: <b><u>{role[0]}</u></b>\nПоточний опис ролі «{name_of_role}»: <b><u>{text_of_role[0]}</u></b>\n\nБот буде надсилати назву ролі та її опис без жирного шрифту та без підкреслення.\n\n⬇️Виберіть що ви хочете змінити⬇️", 
                                    reply_markup=control_keyboard, 
                                    parse_mode="html")

    @router_construct_event.callback_query(F.data == "name_of_role")
    async def name_of_role_callback_query(callback: CallbackQuery):
        global is_input_name_of_role
        go_to_role_menu_button = InlineKeyboardButton(text="⬅️ Назад ⬅️", callback_data="go_to_role_menu")

        control_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [go_to_role_menu_button]
        ])
        await callback.message.edit_text(f"Напиши мені нову назву для ролі «{name_of_role}»", reply_markup=control_keyboard)

        is_input_name_of_role = True


    @router_construct_event.callback_query(F.data == "description_of_role")
    async def name_of_role_callback_query(callback: CallbackQuery):
        global is_input_description_of_role
        go_to_role_menu_button = InlineKeyboardButton(text="⬅️ Назад ⬅️", callback_data="go_to_role_menu")

        control_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [go_to_role_menu_button]
        ])
        await callback.message.edit_text(f"Напиши мені новий опис для ролі «{name_of_role}»", reply_markup=control_keyboard)

        is_input_description_of_role = True


    @router_construct_event.message(lambda message: is_input_name_of_role)
    async def is_input_name_of_role_cmd(message: Message):
        global is_input_name_of_role
        cursor.execute(f"UPDATE admin_panel SET {role_in_db} = %s WHERE creator_id = %s AND group_id = %s", (message.text, message.from_user.id, chat_id))
        conn.commit()

        success_message = await message.answer(f"Назву ролі «{name_of_role}» змінено на: <u><b>{message.text}</b></u>", parse_mode="html")
        is_input_name_of_role = False

        await asyncio.sleep(7)

        await success_message.delete()
        await message.delete()


    @router_construct_event.message(lambda message: is_input_description_of_role)
    async def is_input_name_of_role_cmd(message: Message):
        global is_input_description_of_role
        cursor.execute(f"UPDATE admin_panel SET {role_in_db}_text = %s WHERE creator_id = %s AND group_id = %s", (message.text, message.from_user.id, chat_id))
        conn.commit()

        success_message = await message.answer(f"Опис ролі «{name_of_role}» змінено на: <u><b>{message.text}</b></u>", parse_mode="html")
        is_input_description_of_role = False

        await asyncio.sleep(7)

        await success_message.delete()
        await message.delete()


    @router_construct_event.callback_query(F.data == "go_to_role_menu")
    async def go_to_main_menu_callback_query(callback: CallbackQuery):
        global is_input_name_of_role
        is_input_name_of_role = False

        cursor.execute(f"SELECT {role_in_db} FROM admin_panel WHERE creator_id = %s AND group_id = %s", (callback.from_user.id, chat_id))
        role = cursor.fetchone()

        cursor.execute(f"SELECT {role_in_db}_text FROM admin_panel WHERE creator_id = %s AND group_id = %s", (callback.from_user.id, chat_id))
        text_of_role = cursor.fetchone()

        go_to_main_menu_button = InlineKeyboardButton(text="⬅️ Назад ⬅️", callback_data="go_to_main_menu")
        name_of_role_button = InlineKeyboardButton(text="Назву ролі", callback_data="name_of_role")
        description_of_role_button = InlineKeyboardButton(text="Опис ролі", callback_data="description_of_role")

        control_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [name_of_role_button],
            [description_of_role_button],
            [go_to_main_menu_button]
        ])

        await callback.message.edit_text(text=f"Поточна назва ролі «{name_of_role}»: <b><u>{role[0]}</u></b>\nПоточний опис ролі «{name_of_role}»: <b><u>{text_of_role[0]}</u></b>\n\nБот буде надсилати назву ролі та її опис без жирного шрифту та без підкреслення.\n\n⬇️Виберіть що ви хочете змінити⬇️", 
                                        reply_markup=control_keyboard, 
                                        parse_mode="html")


@router_construct_event.callback_query(F.data == "doctor")
async def doctor_callback_query(callback: CallbackQuery):
    global group_id
    await change_name_of_role(callback=callback, name_of_role="Лікар", role_in_db="doctor", chat_id=group_id)


@router_construct_event.callback_query(F.data == "all_capone")
async def doctor_callback_query(callback: CallbackQuery):
    global group_id
    await change_name_of_role(callback=callback, name_of_role="Аль Капоне", role_in_db="all_capone", chat_id=group_id)


@router_construct_event.callback_query(F.data == "civilian")
async def doctor_callback_query(callback: CallbackQuery):
    global group_id
    await change_name_of_role(callback=callback, name_of_role="Мирний Житель", role_in_db="civilian", chat_id=group_id)


@router_construct_event.callback_query(F.data == "go_to_main_menu")
async def go_to_main_menu_callback_query(callback: CallbackQuery):
    doctor_button = InlineKeyboardButton(text="Лікар", callback_data="doctor")
    all_capone_button = InlineKeyboardButton(text="Аль Капоне", callback_data="all_capone")
    civilian_button = InlineKeyboardButton(text="Мирний житель", callback_data="civilian")
    add_group_button = InlineKeyboardButton(text="➕ Додати групу ➕", callback_data="add")
    delete_group_button = InlineKeyboardButton(text="❌ Видалити групу ❌", callback_data="delete")

    roles_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [doctor_button],
        [all_capone_button],
        [civilian_button],
        [add_group_button],
        [delete_group_button]
    ])

    await callback.message.edit_text("⬇️ Вибери яку роль ти хочеш змінити ⬇️", reply_markup=roles_buttons)


@router_construct_event.callback_query(F.data == "add_group")
async def add_group(callback: CallbackQuery):
    global is_input_add_chat_id

    await callback.message.edit_text("Надішли мені айді групи в якій <u><b>ти власник</b></u>", parse_mode="html")

    is_input_add_chat_id = True


@router_construct_event.message(lambda message: is_input_add_chat_id)
async def IsInputAddChatId(message: Message, bot: Bot):
    global is_input_add_chat_id
    try:
        chat_id = int(message.text)

        cursor.execute("SELECT group_id FROM admin_panel")
        group_ids = [row[0] for row in cursor.fetchall()]

        if chat_id in group_ids:
            await message.answer("Це id групи вже є в базі, введіть інше")
        else:
            chat_member = await bot.get_chat_member(chat_id, message.from_user.id)

            status = chat_member.status

            if status == ChatMemberStatus.CREATOR:
                cursor.execute("INSERT INTO admin_panel (creator_id, group_id) VALUES (%s, %s)", (message.from_user.id, chat_id))
                conn.commit()

                chat = await bot.get_chat(chat_id=chat_id)

                await message.answer(f"Ти зареєстрований як власник групи: {chat.title}\nТепер відправ команду /construct_event ще раз!")

                is_input_add_chat_id = False
            else:
                await message.answer("Ти не є власником групи!")
                is_input_add_chat_id = False

    except ValueError:
        await message.answer("Напиши айді групи воно складається з цифр без букв")


@router_construct_event.callback_query(F.data == "delete_group")
async def delete_group(callback: CallbackQuery):
    yes_button = InlineKeyboardButton(text="Так", callback_data="yes")
    no_button = InlineKeyboardButton(text="Ні", callback_data="no")

    yes_or_no_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [yes_button],
        [no_button]
    ])

    await callback.message.edit_text("Ти точно хочеш видалити групу?", reply_markup=yes_or_no_buttons)


@router_construct_event.callback_query(F.data == "yes")
async def yes_callback(callback: CallbackQuery, bot: Bot):
    name_of_add_chats = []
    cursor.execute("SELECT group_id FROM admin_panel WHERE creator_id = %s", (callback.from_user.id,))
    group_ids = cursor.fetchall()[0]

    list_of_chats = InlineKeyboardBuilder()

    for chat_id in group_ids:
        print(group_ids)
        chat = await bot.get_chat(chat_id=int(chat_id))

        list_of_chats.button(text=f"{chat.title}", callback_data=f"{chat.title}_delete")
        
        list_of_chats.adjust(1)

        name_of_add_chats.append((chat_id, chat.title))

    print("1:", name_of_add_chats)

    await callback.message.edit_text("Вибери чат який видалиш зі списку", reply_markup=list_of_chats.as_markup())
    
    for id, title in name_of_add_chats:
        @router_construct_event.callback_query(F.data == f"{title}_delete")
        async def delete_chat(callback: CallbackQuery):
            global name_of_add_chats

            print("2:", name_of_add_chats)

            cursor.execute("DELETE FROM admin_panel WHERE creator_id = %s AND group_id = %s", (callback.from_user.id, id))
            conn.commit()

            await callback.message.edit_text(f"Чат {title} видалено! Ви будь-коли зможете його додати")

            name_of_add_chats.remove((id, title))


@router_construct_event.callback_query(F.data == "no")
async def no_callback(callback: CallbackQuery, bot: Bot):
    cursor.execute("SELECT group_id FROM admin_panel WHERE creator_id = %s", (callback.from_user.id,))
    group_ids = cursor.fetchall()

    list_of_chats = InlineKeyboardBuilder()

    for chat_id in group_ids:
        chat = await bot.get_chat(chat_id=int(chat_id[0]))

        list_of_chats.button(text=f"{chat.title}", callback_data=chat.title)
        
        list_of_chats.adjust(1)

    await callback.message.edit_text("Вибери чат де будеш будувати івент", reply_markup=list_of_chats.as_markup())


@router_construct_event.callback_query(F.data == "default")
async def default_settings(callback: CallbackQuery):
    list = [("Чи любиш ти пити каву зранку?", "question_for_civilian_1", "Так", "Ні"), 
            ("Чи вмієш ти готувати яєчню?", "question_for_civilian_2", "Так", "Ні"), 
            ("Ти віддаєш перевагу перегляду фільмів вдома, чи кінотеатрі?", "question_for_civilian_3", "Вдома", "В кінотеатрі"),
            ("Ти полюбляєш вечірні прогулянки?", "question_for_civilian_4", "Так", "Ні"), 
            ("Ти за паперові чи електронні книги?", "question_for_civilian_5", "Паперові", "Електронні"), 
            ("Ти слухаєш подкасти?", "question_for_civilian_6", "Так", "Ні"), 
            ("Ти маєш улюблену музичну групу, чи виконавців?", "question_for_civilian_7", "Так", "Ні"),
            ("Чи часто ти відвідуєш музеї/виставки?", "question_for_civilian_8", "Так", "Ні"), 
            ("У тебе є домашні улюбленці?", "question_for_civilian_9", "Так", "Ні"), 
            ("Любиш подорожі на велосипеді?", "question_for_civilian_10", "Так", "Ні"),
            ("Лікар", "doctor", "1", "2"),
            ("Цієї гри ти - Лікар!\nРоби все, щоб врятувати якомога більше мирних людей.", "doctor_text", "1", "2"),
            ("Аль Капоне", "all_capone", "1", "2"),
            ("Цієї гри ти - Аль Капоне!\nРоби все, щоб твоя сім`я отримала перемогу, над цими нікчемними мирними жителями.", "all_capone_text", "1", "2"),
            ("Цієї гри ти - Мирний житель!\nРоби все, щоб знищити підступне угрупування Аль Капоне.", "civilian_text", "1", "2"),
            ("Мирний Житель", "civilian", "1", "2")]

    for text, column, answer1, answer2 in list:
        cursor.execute(f"UPDATE admin_panel SET {column} = %s WHERE creator_id = %s AND group_id = %s", (text, callback.from_user.id, chat_id))
        conn.commit()

    await callback.message.edit_text("Скинуто все до початкових змін!")