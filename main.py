import logging
from aiogram import Bot, Dispatcher, executor, types
import os

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Данные шагов
steps = [
    80,  # шаг 1 — 1ч 20м
    45,  # шаг 2 — 45м
    60,  # шаг 3 — 1ч
    70,  # шаг 4 — 1ч 10м
    90,  # шаг 5 — 1ч 30м
    100, # шаг 6 — 1ч 40м
    110, # шаг 7 — 1ч 50м
    120, # шаг 8 — 2ч
    130, # шаг 9 — 2ч 10м
    140, # шаг 10 — 2ч 20м
    150, # шаг 11 — 2ч 30м
    150  # шаг 12 — 2ч 30м
]

def format_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours == 0:
        return f"{mins}м"
    elif mins == 0:
        return f"{hours}ч"
    else:
        return f"{hours}ч {mins}м"

def generate_step_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, 12, 2):
        row = []
        for j in range(2):
            if i + j < len(steps):
                label = f"Шаг {i+j+1} ({format_duration(steps[i+j])})"
                row.append(types.KeyboardButton(label))
        markup.row(*row)
    markup.add(types.KeyboardButton("ℹ️ Инфо"))
    return markup

INFO_TEXT = """ℹ️ Инфо
Метод суперкомпенсации — это пошаговая схема загара.
Ты выбираешь шаг — и загораешь строго по таймингу.

Начинать всегда нужно с шага 1, даже если ты уже немного загорел(а).
Каждый новый день или после перерыва — возвращайся на 2 шага назад.

Так кожа адаптируется к солнцу — и ты загораешь равномерно, без ожогов.
Это снижает риск пятен, перегрева и помогает телу включать защиту:
меланин, гормоны адаптации и иммунный ответ.

🌤️ Рекомендуем загорать:
с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,
и при отсутствии противопоказаний можно загорать без SPF.

☀️ С 11:00 до 17:00 — солнце агрессивнее.
Если остаёшься на улице — надевай одежду, головной убор или используй SPF.

Если есть вопросы — пиши: @sunxbeach_director"""

WELCOME_TEXT = """Привет, солнце! ☀️
Ты в таймере по методу суперкомпенсации.
Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.

Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.
Каждый новый день и после перерыва — возвращайся на 2 шага назад.

Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."""

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=generate_step_keyboard())

@dp.message_handler(lambda message: message.text == "ℹ️ Инфо")
async def show_info(message: types.Message):
    await message.answer(INFO_TEXT)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
