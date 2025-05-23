import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from steps import steps

API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}
tasks = {}

def step_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    buttons = []
    for step in steps:
        total_min = sum(p['duration_min'] for p in step['positions'])
        h = int(total_min // 60)
        m = int(total_min % 60)
        label = f"Шаг {step['step']} ({f'{h}ч ' if h else ''}{m}м)"
        buttons.append(KeyboardButton(label))
    for i in range(0, len(buttons), 4):
        kb.add(*buttons[i:i+4])
    kb.add(KeyboardButton("ℹ️ Инфо"))
    return kb

def control_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏭️ Пропустить")
    kb.add("⛔ Завершить")
    kb.add("↩️ Назад на 2 шага")
    kb.add("📋 Вернуться к шагам")
    return kb

def finish_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏭️ Продолжить", "⛔ Завершить")
    kb.add("↩️ Назад на 2 шага", "📋 Вернуться к шагам")
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        '''Привет, солнце! ☀️
Ты в таймере по методу суперкомпенсации.
Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.
Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,
регуляцию гормонов и укрепление иммунной системы.

Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.
Каждый новый день и после перерыва — возвращайся на 2 шага назад.

Хочешь разобраться подробнее — жми ℹ️ Инфо.''',
        reply_markup=step_keyboard()
    )

@dp.message_handler(lambda m: m.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.
"
        "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.

"
        "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,
"
        "и при отсутствии противопоказаний можно загорать без SPF.
"
        "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.

"
        "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF.

"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.
"
        "Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.

"
        "Если есть вопросы — пиши: @sunxbeach_director"
    )