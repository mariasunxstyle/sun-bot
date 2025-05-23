# main.py (упрощённый шаблон, допиши в нужной логике)
from aiogram import Bot, Dispatcher, executor, types
import logging
import os
from steps import steps

API_TOKEN = os.getenv("TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет, солнце! ☀️")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
