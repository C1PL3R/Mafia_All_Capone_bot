from aiogram import Router, F, Bot
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice, ErrorEvent
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
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


class DonateCommand:
    def __init__(self):
        self.router_donate = Router()

        self.router_donate.message.register(self.buy_subscription_handler, Command("buy_subscription"))
        self.router_donate.message.register(self.stop_subscription_handler, Command("stop_subscription"))
        self.router_donate.message.register(self.refund_handler, lambda message: self.is_refund)
        self.router_donate.errors.register(self.errors_handler)
        self.router_donate.message.register(self.success_donate_handler, F.successful_payment)
        self.router_donate.pre_checkout_query.register(self.pre_checkout_handler)

        self.is_refund = False


    async def buy_subscription_handler(self, message: Message):
        print(message.effect_id)
        await message.answer_invoice(
            title="Продовжити або купити підписку",
            description="Ця підписка допоможе тобі користуватися ботом у своїх чатах",
            prices=[LabeledPrice(label="XTR", amount=1)],
            provider_token="",
            currency="XTR",
            payload="Pay",
            protect_content=True,
            message_effect_id="5159385139981059251"
        )


    async def pre_checkout_handler(self, pre_checkout: PreCheckoutQuery):
        await pre_checkout.answer(ok=True)


    async def success_donate_handler(self, message: Message):
        await message.answer(text="Оплата пройшла успішно!",
                             protect_content=True, message_effect_id="5046509860389126442")


    async def stop_subscription_handler(self, message: Message, bot: Bot):
        await message.answer("Надай id транзакції за для її повернення", protect_content=True, message_effect_id="5104841245755180586")
        self.is_refund = True


    async def refund_handler(self, message: Message, bot: Bot):
        await bot.refund_star_payment(user_id=message.from_user.id, telegram_payment_charge_id=message.text)

        await message.answer("Твої зірочки повернені!", protect_content=True, message_effect_id="5104841245755180586")
        self.is_refund = False


    async def errors_handler(self, error: ErrorEvent):
        exception = error.exception
        update = error.update
        if isinstance(exception, TelegramBadRequest):
            if "CHARGE_NOT_FOUND" in str(exception):
                await update.message.answer("Цю транзакцію я не виконував!", protect_content=True)
            elif "CHARGE_ALREADY_REFUNDED" in str(exception):
                await update.message.answer("За цю транзакцію я зірки віддав!", protect_content=True)
    
