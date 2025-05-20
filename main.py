
import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from steps import steps

import os
API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_state = {}

WELCOME_TEXT = (
    "Привет, солнце! ☀️\n"
    "Ты в таймере по методу суперкомпенсации.\n"
    "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n"
    "Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,\n"
    "регуляцию гормонов и укрепление иммунной системы.\n\n"
    "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n\n"
    "Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."
)

INFO_TEXT = (
    "ℹ️ Инфо\n"
    "Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
    "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
    "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,\n"
    "и при отсутствии противопоказаний можно загорать без SPF.\n"
    "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
    "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице —\n"
    "надевай одежду, головной убор или используй SPF.\n\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n"
    "Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.\n\n"
    "Если есть вопросы — пиши: @sunxbeach_director"
)

def step_keyboard():
    buttons = []
    for s in steps:
        h = int(sum(p['duration_min'] for p in s['positions']) // 60)
        m = int(sum(p['duration_min'] for p in s['positions']) % 60)
        label = f"Шаг {s['step']} ("
        label += f"{h}ч " if h else ""
        label += f"{m}м)"
        buttons.append(types.KeyboardButton(label))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    keyboard.add(*buttons)
    keyboard.add(types.KeyboardButton("ℹ️ Инфо"))
    return keyboard

def control_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏭️ Пропустить")
    kb.add("⛔ Завершить")
    kb.add("↩️ Назад на 2 шага")
    kb.add("📋 Вернуться к шагам")
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=step_keyboard())

@dp.message_handler(lambda msg: "Шаг" in msg.text and "(" in msg.text)
async def select_step(message: types.Message):
    try:
        match = re.search(r"Шаг (\d+)", message.text)
        if not match:
            await message.answer("⚠️ Не смог распознать шаг.")
            return
        step_num = int(match.group(1))
        step_data = next((s for s in steps if s["step"] == step_num), None)
        if not step_data:
            await message.answer(f"⚠️ Шаг {step_num} не найден.")
            return
        user_state[message.from_user.id] = {"step": step_num, "pos": 0}
        await run_step(message.chat.id, message.from_user.id)
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске шага: {str(e)}")

@dp.message_handler(lambda msg: msg.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(INFO_TEXT)

@dp.message_handler(lambda msg: msg.text in ["⏭️ Пропустить", "↩️ Назад на 2 шага", "⛔ Завершить", "📋 Вернуться к шагам"])
async def handle_controls(message: types.Message):
    uid = message.from_user.id
    if uid not in user_state:
        await message.answer("Сначала выбери шаг.")
        return

    if message.text == "↩️ Назад на 2 шага":
        current = user_state[uid]["step"]
        new_step = max(1, current - 2)
        user_state[uid] = {"step": new_step, "pos": 0}
        await run_step(message.chat.id, uid)
    elif message.text == "⏭️ Пропустить":
        user_state[uid]["pos"] += 1
        await run_step(message.chat.id, uid)
    elif message.text == "📋 Вернуться к шагам":
        await message.answer("Выбери шаг:", reply_markup=step_keyboard())
    elif message.text == "⛔ Завершить":
        del user_state[uid]
        await message.answer("Сеанс завершён. Можешь вернуться позже ☀️", reply_markup=step_keyboard())

async def run_step(chat_id, uid):
    state = user_state[uid]
    step = next(s for s in steps if s["step"] == state["step"])
    if state["pos"] >= len(step["positions"]):
        await bot.send_message(chat_id, "Шаг завершён ✅", reply_markup=control_keyboard())
        return
    pos = step["positions"][state["pos"]]
    await bot.send_message(chat_id, f"{pos['name']} — {pos['duration_min']} мин", reply_markup=control_keyboard())
    await asyncio.sleep(pos['duration_min'] * 60)
    user_state[uid]["pos"] += 1
    await run_step(chat_id, uid)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
