import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from steps import steps
import asyncio

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_state = {}  # {user_id: {"step": 1, "pos": 0, "message_id": int}}

WELCOME_TEXT = """Привет, солнце! ☀️
Ты в таймере по методу суперкомпенсации.
Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.

Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.
Каждый новый день и после перерыва — возвращайся на 2 шага назад.

Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."""

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

def step_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, 12, 4):
        row = []
        for j in range(4):
            idx = i + j
            if idx < len(steps):
                s = steps[idx]
                total = sum(p['duration_min'] for p in s['positions'])
                h = int(total) // 60
                m = int(total) % 60
                label = f"{h}ч {m}м" if h else f"{m}м"
                row.append(types.KeyboardButton(f"Шаг {s['step']} ({label})"))
        kb.row(*row)
    kb.add(types.KeyboardButton("ℹ️ Инфо"))
    return kb

def control_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏭️ Пропустить")
    kb.add("⛔ Завершить")
    kb.add("↩️ Назад на 2 шага")
    kb.add("📋 Вернуться к шагам")
    return kb


    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"))
    kb.add(InlineKeyboardButton("⛔ Завершить", callback_data="stop"))
    kb.add(InlineKeyboardButton("↩️ Назад на 2 шага", callback_data="back2"))
    kb.add(InlineKeyboardButton("📋 Вернуться к шагам", callback_data="back_to_menu"))
    return kb

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=step_keyboard())

@dp.message_handler(lambda msg: msg.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(INFO_TEXT)

@dp.message_handler(lambda msg: msg.text.startswith("Шаг "))
@dp.message_handler(lambda msg: msg.text in ["⏭️ Пропустить", "⛔ Завершить", "↩️ Назад на 2 шага", "📋 Вернуться к шагам"])
async def start_step(message: types.Message):
    try:
        step_num = int(message.text.split()[1])
        step_data = next(s for s in steps if s["step"] == step_num)
        user_state[message.from_user.id] = {"step": step_num, "pos": 0}
        await start_position_loop(message.chat.id, message.from_user.id)
    except:
        await message.answer("Не удалось запустить шаг. Попробуй ещё раз.")

async def start_position_loop(chat_id, user_id):
    state = user_state[user_id]
    step = next(s for s in steps if s["step"] == state["step"])
    if state["pos"] == 0:
        
        await asyncio.sleep(int(pos["duration_min"] * 60))
        if user_state.get(user_id) is None:
            return
        state["pos"] += 1
    await bot.send_message(chat_id, "Шаг завершён ✅", reply_markup=step_keyboard())
    user_state.pop(user_id, None)

@dp.callback_query_handler(lambda c: c.data)
async def handle_controls(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    data = callback.data
    state = user_state.get(user_id)

    if data == "skip" and state:
        state["pos"] += 1
        await start_position_loop(chat_id, user_id)
    elif data == "stop":
        user_state.pop(user_id, None)
        await bot.send_message(chat_id, "Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=exit_keyboard())
    elif data == "back2":
        if state:
            new_step = max(1, state["step"] - 2)
            user_state[user_id] = {"step": new_step, "pos": 0}
            await start_position_loop(chat_id, user_id)
    elif data == "back_to_menu":
        await bot.send_message(chat_id, "Выбери шаг 👇", reply_markup=step_keyboard())
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
