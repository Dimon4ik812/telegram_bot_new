from aiogram import F, types, Router, Bot

from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user, orm_get_user_carts,
)

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack, get_callback_btns



user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))



@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.")


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):

    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


# # Добавляем новый обработчик для кнопки "Заказать"
# @user_private_router.callback_query(F.data == "order")
# async def handle_order(callback: types.CallbackQuery, session: AsyncSession):
#     # Создаем клавиатуру с выбором действий
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton("Выбрать способ оплаты", callback_data="choose_payment")],
#         [types.InlineKeyboardButton("Отправить контакты", callback_data="send_contacts")]
#     ])
#
#     await callback.message.answer(
#         "Как вы хотите оформить заказ?",
#         reply_markup=keyboard
#     )
#     await callback.answer()
#
#
# # Обработчик выбора способа оплаты
# @user_private_router.callback_query(F.data == "choose_payment")
# async def choose_payment_method(callback: types.CallbackQuery, session: AsyncSession):
#     # Создаем клавиатуру с вариантами оплаты
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton("Картой онлайн", callback_data="pay_online")],
#         [types.InlineKeyboardButton("Наличными при получении", callback_data="pay_cash")]
#     ])
#
#     await callback.message.answer(
#         "Выберите способ оплаты:",
#         reply_markup=keyboard
#     )
#     await callback.answer()
#
#
# # Добавьте обработчики для каждого способа оплаты
# @user_private_router.callback_query(F.data == "pay_online")
# async def pay_online(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.message.answer("Вы выбрали оплату картой онлайн. Перейдите к оплате.")
#     await callback.answer()
#
#
# @user_private_router.callback_query(F.data == "pay_cash")
# async def pay_cash(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.message.answer("Вы выбрали оплату наличными при получении.")
#     await callback.answer()
#
#
# # Обработчик отправки контактов
# @user_private_router.callback_query(F.data == "send_contacts")
# async def send_contacts(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
#     user_id = callback.from_user.id
#
#     # Отправляем запрос на предоставление контактов
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(types.KeyboardButton("Отправить контакт", request_contact=True))
#
#     await callback.message.answer(
#         "Пожалуйста, отправьте свои контактные данные, чтобы мы могли связаться с вами.",
#         reply_markup=keyboard
#     )
#     await callback.answer()
#
#
# # Обработчик получения контактов
# @user_private_router.message(F.contact)
# async def process_contact(message: types.Message, bot: Bot, session: AsyncSession):
#     contact = message.contact
#
#     # Сохраняем контакты пользователя в базу данных
#     await orm_add_user(
#         session,
#         user_id=contact.user_id,
#         first_name=contact.first_name,
#         last_name=contact.last_name,
#         phone=contact.phone_number
#     )
#
#     # Отправляем уведомление менеджеру
#     manager_chat_id = '1154730701' # Замените на ID чата менеджера
#     await bot.send_message(
#         manager_chat_id,
#         f"Поступил новый заказ!\n"
#         f"Имя: {contact.first_name}\n"
#         f"Телефон: {contact.phone_number}"
#     )
#
#     await message.answer(
#         "Спасибо! Менеджер свяжется с вами в ближайшее время.",
#         reply_markup=types.ReplyKeyboardRemove()
#     )

@user_private_router.callback_query(F.data == "order")
async def handle_order(callback: types.CallbackQuery, session: AsyncSession):
    # Создаем клавиатуру с выбором действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать способ оплаты", callback_data="choose_payment")],
        [InlineKeyboardButton(text="Оставить контакты", callback_data="leave_contacts")]
    ])

    await callback.message.answer(
        "Как вы хотите оформить заказ?",
        reply_markup=keyboard
    )
    await callback.answer()



@user_private_router.callback_query(F.data == "choose_payment")
async def choose_payment_method(callback: types.CallbackQuery, session: AsyncSession):
    # Создаем клавиатуру с вариантами оплаты
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Картой онлайн", callback_data="pay_online")],
        [InlineKeyboardButton(text="Наличными при получении", callback_data="pay_cash")]
    ])

    await callback.message.answer(
        "Выберите способ оплаты:",
        reply_markup=keyboard
    )
    await callback.answer()



@user_private_router.callback_query(F.data == "pay_online")
async def pay_online(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer("Перейдите к оплате картой онлайн.")
    await callback.answer()

@user_private_router.callback_query(F.data == "pay_cash")
async def pay_cash(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer("Вы выбрали оплату наличными при получении.")
    await callback.answer()


@user_private_router.callback_query(F.data == "leave_contacts")
async def leave_contacts(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
    # Создаем клавиатуру с кнопкой отправки контактов
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await callback.message.answer(
        "Пожалуйста, отправьте свои контактные данные, чтобы мы могли связаться с вами.",
        reply_markup=keyboard
    )
    await callback.answer()


@user_private_router.message(F.contact)
async def process_contact(message: types.Message, session: AsyncSession, bot: Bot):
    contact = message.contact
    user_id = contact.user_id

    # Сохраняем контакты пользователя в базу данных
    await orm_add_user(
        session,
        user_id=user_id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone=contact.phone_number
    )

    # Получаем содержимое корзины пользователя
    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        await message.answer("Корзина пуста! Сначала добавьте товары.")
        return

    # Формируем детали заказа
    order_details = "Детали заказа:\n"
    total_price = 0
    for cart in carts:
        product_name = cart.product.name
        quantity = cart.quantity
        price = round(cart.product.price * quantity, 2)
        total_price += price
        order_details += f"• {product_name} x {quantity} = {price} руб.\n"

    order_details += f"\nОбщая стоимость: {total_price} руб."

    # Отправляем уведомление менеджеру
    manager_chat_id = "1154730701" # Замените на ID чата менеджера
    contact_info = (
        f"Поступил новый заказ!\n"
        f"Имя: {contact.first_name}\n"
        f"Телефон: {contact.phone_number}\n\n"
    )
    full_message = contact_info + order_details

    await bot.send_message(
        chat_id=manager_chat_id,
        text=full_message
    )

    await message.answer(
        "Спасибо! Менеджер свяжется с вами в ближайшее время.",
        reply_markup=types.ReplyKeyboardRemove()  # Убираем клавиатуру после отправки контактов
    )