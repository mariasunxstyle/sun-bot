
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from steps import steps

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "sunxstyle"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

WELCOME_TEXT = (
    "Привет, солнце! ☀️\n"
    "Ты в таймере по методу суперкомпенсации.\n"
    "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n"
    "Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,\n"
    "регуляцию гормонов и укрепление иммунной системы.\n\n"
    "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n\n"
    "Хочешь разобраться подробнее — жми ℹ️ Инфо."
)

INFO_TEXT = (
    "ℹ️ Инфо\n"
    "Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
    "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
    "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,\n"
    "и при отсутствии противопоказаний можно загорать без SPF.\n"
    "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
    "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице — надевай одежду, головной убор или используй SPF.\n\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n"
    "Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.\n\n"
    "Если есть вопросы — пиши: @sunxbeach_director"
)

user_state = {}
tasks = {}

def format_time(mins):
    if mins < 1:
        return f"{int(mins * 60)} сек"
    h = int(mins // 60)
    m = int(mins % 60)
    return f"{h}ч {m}м" if h else f"{m}м"

def step_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for step in steps:
        total = sum(p['duration_min'] for p in step["positions"])
        label = f"Шаг {step['step']} ({format_time(total)})"
        markup.insert(types.KeyboardButton(label))
    markup.add("ℹ️ Инфо")
    return markup

def control_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⏭️ Пропустить")
    markup.add("⛔ Завершить")
    markup.add("↩️ Назад на 2 шага")
    markup.add("📋 Вернуться к шагам")
    return markup

def finish_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⏭️ Продолжить", "⛔ Завершить")
    markup.add("↩️ Назад на 2 шага", "📋 Вернуться к шагам")
    return markup

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def run_step(chat_id, uid):
    state = user_state[uid]
    step = steps[state["step"] - 1]
    pos_idx = state["pos"]

    if pos_idx >= len(step["positions"]):
        await bot.send_message(chat_id, f"Шаг {state['step']} завершён!", reply_markup=finish_keyboard())
        return

    pos = step["positions"][pos_idx]
    await bot.send_message(chat_id, f"{pos['name']} — {format_time(pos['duration_min'])}", reply_markup=control_keyboard())

    await asyncio.sleep(int(pos['duration_min'] * 60))

    state["pos"] += 1
    tasks[uid] = asyncio.create_task(run_step(chat_id, uid))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🔄 Проверить ещё раз"))
        return await message.answer(
            "Бот работает только для подписчиков канала @sunxstyle.\n\nПожалуйста, подпишись — и нажми «🔄 Проверить ещё раз»", reply_markup=kb)
    await message.answer(WELCOME_TEXT, reply_markup=step_keyboard())

@dp.message_handler(lambda m: m.text == "🔄 Проверить ещё раз")
async def check_again(message: types.Message):
    if await is_subscribed(message.from_user.id):
        await message.answer("Готово! ☀️", reply_markup=step_keyboard())
    else:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(types.KeyboardButton("🔄 Проверить ещё раз"))
        await message.answer("Бот работает только для подписчиков канала @sunxstyle.\n\nПожалуйста, подпишись — и нажми «🔄 Проверить ещё раз»", reply_markup=kb)

@dp.message_handler()
async def handle_step(message: types.Message):
    uid = message.from_user.id

    if message.text.startswith("Шаг"):
        step_num = int(message.text.split()[1])
        user_state[uid] = {"step": step_num, "pos": 0}
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))

    elif message.text == "↩️ Назад на 2 шага":
        current = user_state.get(uid, {"step": 3})["step"]
        step_num = max(1, current - 2)
        user_state[uid] = {"step": step_num, "pos": 0}
        await message.answer(f"Шаг {step_num}")
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))

    elif message.text == "📋 Вернуться к шагам":
        await message.answer(reply_markup=step_keyboard())

    elif message.text == "⏭️ Пропустить":
        if uid in user_state:
            user_state[uid]["pos"] += 1
            tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))

    elif message.text == "⛔ Завершить":
        await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=step_keyboard())

    elif message.text == "⏭️ Продолжить":
        user_state[uid]["step"] += 1
        user_state[uid]["pos"] = 0
        await message.answer(f"Шаг {user_state[uid]['step']}")
        tasks[uid] = asyncio.create_task(run_step(message.chat.id, uid))

    elif message.text == "ℹ️ Инфо":
        await message.answer(INFO_TEXT)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
