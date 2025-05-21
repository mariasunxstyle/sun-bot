
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, executor
import os
from steps import steps

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_state = {}
tasks = {}

def format_duration(dur):
    minutes = int(dur)
    hours = minutes // 60
    mins = minutes % 60
    if dur != int(dur):
        return f"{dur} мин"
    elif hours:
        return f"{hours}ч {mins}м" if mins else f"{hours}ч"
    else:
        return f"{mins} мин"

def step_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for step in steps:
        total = sum(p['duration_min'] for p in step['positions'])
        label = f"Шаг {step['step']} ({format_duration(total)})"
        keyboard.insert(types.KeyboardButton(label))
    keyboard.add(types.KeyboardButton("ℹ️ Инфо"))
    return keyboard

def control_keyboard():
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton("⏭️ Продолжить")
    ).add(
        types.KeyboardButton("⛔ Завершить")
    ).add(
        types.KeyboardButton("↩️ Назад на 2 шага")
    ).add(
        types.KeyboardButton("📋 Вернуться к шагам")
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    welcome = (
        "Привет, солнце! ☀️\n"
        "Ты в таймере по методу суперкомпенсации.\n"
        "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n"
        "Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,\n"
        "регуляцию гормонов и укрепление иммунной системы.\n\n"
        "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
        "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n"
        "Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."
    )
    await message.answer(welcome, reply_markup=step_keyboard())

@dp.message_handler(lambda m: m.text == "ℹ️ Инфо")
async def info(message: types.Message):
    await message.answer(
        "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
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

async def run_step(chat_id, uid):
    state = user_state[uid]
    step = next((s for s in steps if s["step"] == state["step"]), None)
    if not step:
        return
    if state["pos"] >= len(step["positions"]):
        await bot.send_message(chat_id, "Шаг завершён ✅", reply_markup=control_keyboard())
        return
    pos = step["positions"][state["pos"]]
    await bot.send_message(chat_id, f"{pos['name']} — {format_duration(pos['duration_min'])}", reply_markup=control_keyboard())
    await asyncio.sleep(int(pos["duration_min"] * 60))
    state["pos"] += 1
    await run_step(chat_id, uid)

@dp.message_handler(lambda m: m.text.startswith("Шаг"))
async def handle_step(message: types.Message):
    uid = message.from_user.id
    try:
        step_num = int(message.text.split(" ")[1])
        user_state[uid] = {"step": step_num, "pos": 0}
        if uid in tasks and not tasks[uid].done():
            tasks[uid].cancel()
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))
    except Exception:
        await message.answer("Не удалось загрузить шаг")

@dp.message_handler(lambda m: m.text in ["⏭️ Продолжить", "⛔ Завершить", "↩️ Назад на 2 шага", "📋 Вернуться к шагам"])
async def control(message: types.Message):
    uid = message.from_user.id
    if uid not in user_state:
        await message.answer("Сначала выбери шаг.")
        return
    if message.text == "⏭️ Продолжить":
        current = user_state[uid]['step']
        next_step = current + 1
        if next_step > 12:
            await message.answer("Все шаги завершены!", reply_markup=step_keyboard())
            return
        user_state[uid] = {"step": next_step, "pos": 0}
        await message.answer(f"Шаг {next_step}")
        if uid in tasks and not tasks[uid].done():
            tasks[uid].cancel()
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))
    elif message.text == "⛔ Завершить":
        await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=step_keyboard())
        user_state.pop(uid, None)
        if uid in tasks:
            tasks[uid].cancel()
    elif message.text == "📋 Вернуться к шагам":
        await message.answer("Выбери шаг:", reply_markup=step_keyboard())
    elif message.text == "↩️ Назад на 2 шага":
        current = user_state[uid]['step']
        new_step = max(1, current - 2)
        user_state[uid] = {'step': new_step, 'pos': 0}
        await message.answer(f"Шаг {new_step}")
        if uid in tasks and not tasks[uid].done():
            tasks[uid].cancel()
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
