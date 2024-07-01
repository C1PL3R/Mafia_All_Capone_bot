from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.database import *
from datetime import datetime, timedelta

router_pay = Router()

# @router_pay.message(Command("buy"))
# async def order(message: Message):
#     await message.answer_invoice(
#         title="Тут назва для товару",
#         description="Тут його опис",
#         payload="buy_premium",
#         provider_token="1661751239:TEST:5f6F-WLUs-br4k-RL7m",
#         currency="UAH",
#         prices=[LabeledPrice(
#                 label="Назва товару",
#                 amount=15000
#             )],
#         start_parameter="buy",
#         provider_data=None,
#         need_name=True,
#         need_email=True,
#         need_phone_number=True,
#         need_shipping_address=False,
#         send_phone_number_to_provider=False,
#         send_email_to_provider=False,
#         is_flexible=False,
#         disable_notification=False,
#         protect_content=True,
#         reply_to_message_id=None,
#         allow_sending_without_reply=True,
#         reply_markup=None,
#         request_timeout=15,
#     )

# @router_pay.pre_checkout_query()
# async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# @router_pay.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: Message):
#     await message.answer(text="Оплата пройшла успішно! <blockquote>Ви купили преміум підписку для доступу бота для </blockquote>", parse_mode="html")
#     message_date = message.date

#     one_month_later = message_date + timedelta(days=30)

@router_pay.message(Command("buy"))
async def order(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатити 1 зірочкою", callback_data="one_star")],
        [InlineKeyboardButton(text="Оплатити 2 зірочки", callback_data="two_stars")]
    ])

    await message.answer(text="Вибери як хочеш оплатити", reply_markup=keyboard)

@router_pay.callback_query(F.data == "one_star")
async def one_star(callback: CallbackQuery):
    await callback.message.answer_invoice(
        title="Оплата Зірочками Від Телеграм",
        description="Оплати 1 зірочками",
        prices=[LabeledPrice(label="XTR", amount=1)],
        provider_token="",
        currency="XTR",
        payload="Pay",
        protect_content=True
    )

@router_pay.callback_query(F.data == "two_stars")
async def one_star(callback: CallbackQuery):
    await callback.message.answer_invoice(
        title="Оплата Зірочками Від Телеграм",
        description="Оплати 2 зірочками",
        prices=[LabeledPrice(label="XTR", amount=2)],
        provider_token="",
        currency="XTR",
        payload="Pay",
        protect_content=True
    )

@router_pay.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)

@router_pay.message(F.successful_payment)
async def success_donate_handler(message: Message):
    await message.answer("Оплата пройшла успішно!")

@router_pay.message(Command("paysupport"))
async def pay_support_handler(message: Message):  
    await message.answer(text="Оплата не повертається!")