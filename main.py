import logging
from aiogram import Bot, Dispatcher, executor, types
import os
import asyncio
from steps import steps

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_state = {}

WELCOME_TEXT = """Привет, солнце! ☀️
Ты в таймере по методу суперкомпенсации.
Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.
Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,
регуляцию гормонов и укрепление иммунной системы.

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
    row = []
    for i, s in enumerate(steps):
        total = sum(p['duration_min'] for p in s['positions'])
        h = int(total) // 60
        m = int(total) % 60
        time_str = f"{h}ч {m}м" if h else f"{m}м"
        label = f"{s['step']} ({time_str})"
        row.append(types.KeyboardButton(label))
        if (i + 1) % 4 == 0:
            kb.row(*row)
            row = []
    if row:
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

def exit_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📋 Вернуться к шагам")
    kb.add("↩️ Назад на 2 шага")
    return kb

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=step_keyboard())

@dp.message_handler(lambda msg: msg.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(INFO_TEXT)

@dp.message_handler(lambda msg: msg.text.endswith("м)") and "(" in msg.text)
async def select_step(message: types.Message):
    try:
        step_num = int(message.text.split(" ")[0])
        step_data = next(s for s in steps if s["step"] == step_num)
        user_state[message.from_user.id] = {"step": step_num, "pos": 0}
        await run_step(message.chat.id, message.from_user.id)
    except:
        await message.answer("Ошибка при запуске шага.")

@dp.message_handler(lambda msg: msg.text in ["⏭️ Пропустить", "⛔ Завершить", "↩️ Назад на 2 шага", "📋 Вернуться к шагам"])
async def handle_controls(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    data = message.text
    state = user_state.get(user_id)

    if data == "⏭️ Пропустить" and state:
        state["pos"] += 1
        await run_step(chat_id, user_id)

    elif data == "⛔ Завершить":
        user_state.pop(user_id, None)
        await bot.send_message(chat_id, "Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=exit_keyboard())

    elif data == "↩️ Назад на 2 шага":
        if state:
            new_step = max(1, state["step"] - 2)
            user_state[user_id] = {"step": new_step, "pos": 0}
            await run_step(chat_id, user_id)

    elif data == "📋 Вернуться к шагам":
        await bot.send_message(chat_id, "Выбери шаг 👇", reply_markup=step_keyboard())

async def run_step(chat_id, user_id):
    state = user_state.get(user_id)
    if not state:
        return
    step = next(s for s in steps if s["step"] == state["step"])
    if state["pos"] == 0:
        await bot.send_message(chat_id, f"{state['step']} — старт", reply_markup=control_keyboard())
    while state["pos"] < len(step["positions"]):
        pos = step["positions"][state["pos"]]
        await bot.send_message(chat_id, f"{pos['name']} — {pos['duration_min']} мин")
        await asyncio.sleep(int(pos["duration_min"] * 60))
        if user_state.get(user_id) is None:
            return
        state["pos"] += 1
    await bot.send_message(chat_id, "Шаг завершён ✅", reply_markup=exit_keyboard())
    user_state.pop(user_id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
