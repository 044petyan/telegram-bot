import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

API_TOKEN = '7990953709:AAF6UCImqB4zRhgf4qI2gXaX_XWaTRdofYA'
ADMIN_ID = 1489298852

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

kb_builder = ReplyKeyboardBuilder()
kb_builder.add(KeyboardButton(text="Оставить заявку"))
kb_builder.add(KeyboardButton(text="Информация"))
kb_builder.add(KeyboardButton(text="Помощь"))
keyboard = kb_builder.as_markup(resize_keyboard=True)

waiting_for_request = set()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я простой бот для приёма заявок.\n"
        "Выбери действие из меню ниже.",
        reply_markup=keyboard
    )

@dp.message()
async def main_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if user_id in waiting_for_request:
        waiting_for_request.remove(user_id)
        username = message.from_user.username or message.from_user.full_name
        await bot.send_message(ADMIN_ID, f"Новая заявка от @{username}:\n{text}")
        await message.answer("Спасибо! Ваша заявка отправлена.")
        await message.answer("Вернись в меню, чтобы сделать что-то ещё.", reply_markup=keyboard)
        return

    if text == "Оставить заявку":
        waiting_for_request.add(user_id)
        await message.answer("Напиши свою заявку, и я отправлю её администратору.")
    elif text == "Информация":
        await message.answer("Этот бот помогает оставлять заявки и получать быстрые ответы.")
    elif text == "Помощь":
        await message.answer("Напиши 'Оставить заявку', чтобы отправить запрос администратору.")
    else:
        await message.answer("Пожалуйста, выбери действие из меню.", reply_markup=keyboard)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
