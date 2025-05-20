import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import os

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def get_check_sub_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Я подписан(а)", callback_data="check_sub"))
    return markup

async def is_subscribed(user_id):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{API_TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
        async with session.get(url) as resp:
            data = await resp.json()
            return data.get("result", {}).get("status") in ["member", "creator", "administrator"]

GREETING_TEXT = """Привет, солнце! ☀️
Ты в таймере по методу суперкомпенсации.
Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.
Такой подход снижает риск повреждений и стимулирует естественную выработку витамина D,
регуляцию гормонов и укрепление иммунной системы.

Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.
Каждый новый день и после перерыва — возвращайся на 2 шага назад.

Хочешь разобраться подробнее — жми ℹ️ Инфо. Там всё по делу."""

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if await is_subscribed(user_id):
        await message.answer(GREETING_TEXT)
    else:
        await message.answer("Чтобы пользоваться ботом, подпишись на канал и нажми кнопку ниже 👇", reply_markup=get_check_sub_button())

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def callback_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_subscribed(user_id):
        await bot.send_message(user_id, GREETING_TEXT)
    else:
        await bot.answer_callback_query(callback_query.id, "Похоже, ты всё ещё не подписан(а).", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
