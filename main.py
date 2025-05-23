import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils import is_subscribed
from steps import steps

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHANNEL_USERNAME = "@sunxstyle"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_states = {}

def format_duration(minutes):
    if minutes < 60:
        return f"{int(minutes)}м"
    h = int(minutes) // 60
    m = int(minutes) % 60
    return f"{h}ч {m}м" if m else f"{h}ч"

def steps_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for step in steps:
        duration = sum(p['duration_min'] for p in step["positions"])
        keyboard.insert(KeyboardButton(f"Шаг {step['step']} ({format_duration(duration)})"))
    keyboard.add("ℹ️ Инфо")
    return keyboard

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    if not await is_subscribed(bot, message.from_user.id, CHANNEL_USERNAME):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔁 Проверить ещё раз"))
        await message.answer("Подпишись на канал и нажми кнопку ниже ⬇️", reply_markup=keyboard)
        return
    await message.answer("Выбери шаг:", reply_markup=steps_keyboard())

@dp.message_handler(lambda msg: msg.text.startswith("Шаг "))
async def handle_step(message: types.Message):
    try:
        step_num = int(message.text.split()[1])
        step = next(s for s in steps if s["step"] == step_num)
        user_states[message.from_user.id] = {"step": step_num, "pos": 0}
        await message.answer(f"{step['positions'][0]['name']} — {int(step['positions'][0]['duration_min'])} мин")
    except Exception as e:
        await message.answer("Не удалось загрузить шаг.")

@dp.message_handler(lambda msg: msg.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer("""
ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.
Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.

Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,
и при отсутствии противопоказаний можно загорать без SPF.
Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.

С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице —
надевай одежду, головной убор или используй SPF.

Каждый новый день и после перерыва — возвращайся на 2 шага назад.
Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.

Если есть вопросы — пиши: @sunxbeach_director
""")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
