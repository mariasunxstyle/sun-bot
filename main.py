from aiogram import Bot, Dispatcher, types, executor
import asyncio, os
from steps import steps
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for step in steps:
        label = f"{step['step']} ({format_duration(step['duration_min'])})"
        kb.add(KeyboardButton(label))
    kb.add(KeyboardButton("ℹ️ Инфо"))
    await message.answer("Привет, солнце! ☀️", reply_markup=kb)
def format_duration(mins):
    h = int(mins) // 60
    m = int(mins) % 60
    if h:
        return f"{h}ч {m}м" if m else f"{h}ч"
    return f"{m}м"
if __name__ == '__main__':
    executor.start_polling(dp)
