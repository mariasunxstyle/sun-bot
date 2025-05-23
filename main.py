import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os

API_TOKEN = os.getenv("TOKEN")

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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in range(0, 12, 4):
        keyboard.add(*[f"Шаг {i + 1} ({[8,9,14,25,35,45,56,65,85,110,135,150][i]}м)" for i in range(row, row + 4)])
    keyboard.add("ℹ️ Инфо")
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def send_info(message: types.Message):
    await message.answer(INFO_TEXT)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
