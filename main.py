import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

API_TOKEN = "7856116405:AAFWDJM4yfMydjmnI7m-iYnTdEEbcnq9d9Y"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

WELCOME_TEXT = (
    "Привет, солнце! ☀️\n"
    "Ты в таймере по методу суперкомпенсации.\n"
    "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n"
    "Такой подход снижает риск повреждений и стимулирует выработку витамина D, "
    "регуляцию гормонов и укрепление иммунной системы.\n\n"
    "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n\n"
    "Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."
)

INFO_TEXT = (
    "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
    "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
    "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое, "
    "и при отсутствии противопоказаний можно загорать без SPF.\n"
    "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
    "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — "
    "надевай одежду, головной убор или используй SPF.\n\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад."
)

# ОБНОВЛЁННЫЙ БЛОК /start

async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in range(0, 12, 4):
        keyboard.add(*[f"Шаг {i + 1} ({[8,9,14,25,35,45,56,65,85,110,135,150][i]}м)" for i in range(row, row + 4)])
    keyboard.add("ℹ️ Инфо")
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def send_info(message: types.Message):
    await message.answer(INFO_TEXT)


from aiogram.utils.exceptions import ChatNotFound

CHANNEL_USERNAME = "@sunxstyle"

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "creator", "administrator")
    except ChatNotFound:
        return False

# ОБНОВЛЁННЫЙ БЛОК /start

async def send_welcome(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if not is_subscribed:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Я подписан(а)", callback_data="check_sub"))
        await message.answer("Чтобы пользоваться ботом, подпишись на канал @sunxstyle и нажми кнопку ниже:", reply_markup=markup)
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    keyboard.add(*[f"Шаг {i + 1} ({[8,9,14,25,35,45,56,65,85,110,135,150][i]}м)" for i in range(12)])
    keyboard.add("ℹ️ Инфо")
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def process_callback_check_sub(callback_query: types.CallbackQuery):
    is_subscribed = await check_subscription(callback_query.from_user.id)
    if is_subscribed:
        await bot.answer_callback_query(callback_query.id)
        await send_welcome(callback_query.message)
    else:
        await bot.answer_callback_query(callback_query.id, text="Подписка не найдена. Попробуй ещё раз после подписки.", show_alert=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
