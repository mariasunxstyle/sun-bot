import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
from steps import steps

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Хранилище состояний
user_state = {}

# Кнопки управления во время шага
def control_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("⏭️ Пропустить", callback_data="skip"))
    keyboard.add(InlineKeyboardButton("⛔ Завершить", callback_data="stop"))
    keyboard.add(InlineKeyboardButton("↩️ Назад на 2 шага", callback_data="back2"))
    return keyboard

# Приветствие
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

# Клавиатура шагов
def step_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, 12, 4):
        row = []
        for j in range(4):
            if i + j < len(steps):
                step_num = i + j + 1
                duration = sum(pos['duration_min'] for pos in steps[i + j]['positions'])
                h = int(duration) // 60
                m = int(duration) % 60
                label = f"{h}ч {m}м" if h else f"{m}м"
                row.append(types.KeyboardButton(f"Шаг {step_num} ({label})"))
        keyboard.row(*row)
    keyboard.add(types.KeyboardButton("ℹ️ Инфо"))
    return keyboard

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=step_keyboard())

@dp.message_handler(lambda msg: msg.text == "ℹ️ Инфо")
async def info_handler(message: types.Message):
    await message.answer(INFO_TEXT)

@dp.message_handler(lambda msg: msg.text.startswith("Шаг "))
async def step_selected(message: types.Message):
    try:
        step_num = int(message.text.split()[1])
        step_data = next(s for s in steps if s["step"] == step_num)
        user_state[message.from_user.id] = {"step": step_num, "pos": 0}
        await proceed_next_position(message.from_user.id, message.chat.id)
    except:
        await message.answer("Что-то пошло не так при выборе шага.")

async def proceed_next_position(user_id, chat_id):
    state = user_state.get(user_id)
    if not state:
        return
    step_data = next((s for s in steps if s["step"] == state["step"]), None)
    if not step_data:
        return
    if state["pos"] >= len(step_data["positions"]):
        await bot.send_message(chat_id, "Шаг завершён ✅", reply_markup=step_keyboard())
        user_state.pop(user_id, None)
        return
    pos = step_data["positions"][state["pos"]]
    mins = pos["duration_min"]
    await bot.send_message(chat_id, f"{pos['name']} — {mins} мин", reply_markup=control_keyboard())
    await asyncio.sleep(mins * 60)
    state["pos"] += 1
    await proceed_next_position(user_id, chat_id)

@dp.callback_query_handler(lambda c: c.data in ["skip", "stop", "back2"])
async def callback_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "skip":
        if user_id in user_state:
            user_state[user_id]["pos"] += 1
            await proceed_next_position(user_id, callback.message.chat.id)
    elif callback.data == "stop":
        user_state.pop(user_id, None)
        await callback.message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=step_keyboard())
    elif callback.data == "back2":
        if user_id in user_state:
            user_state[user_id]["step"] = max(1, user_state[user_id]["step"] - 2)
            user_state[user_id]["pos"] = 0
            await proceed_next_position(user_id, callback.message.chat.id)
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
