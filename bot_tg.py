import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
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
kb_builder.add(KeyboardButton(text="Калькулятор"))
keyboard = kb_builder.as_markup(resize_keyboard=True)

waiting_for_request = set()
user_op = {}
waiting_for_numbers = set()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я простой бот с заявками и калькулятором.\n"
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

    if user_id in waiting_for_numbers:
        op = user_op.get(user_id)
        try:
            a, b = map(float, text.split())
        except:
            await message.answer("Ошибка! Введи два числа через пробел, например: 5 3")
            return

        if op == "add":
            res = a + b
        elif op == "sub":
            res = a - b
        elif op == "mul":
            res = a * b
        elif op == "div":
            if b == 0:
                await message.answer("Ошибка! Деление на ноль невозможно.")
                return
            res = a / b
        else:
            await message.answer("Неизвестная операция.")
            waiting_for_numbers.discard(user_id)
            user_op.pop(user_id, None)
            return

        await message.answer(f"Результат: {res}")
        waiting_for_numbers.discard(user_id)
        user_op.pop(user_id, None)
        await message.answer("Вернись в меню, чтобы сделать что-то ещё.", reply_markup=keyboard)
        return

    if text == "Оставить заявку":
        waiting_for_request.add(user_id)
        await message.answer("Напиши свою заявку, и я отправлю её администратору.")
    elif text == "Информация":
        await message.answer("Этот бот помогает оставлять заявки и считать простые выражения.")
    elif text == "Помощь":
        await message.answer("Выбери 'Оставить заявку' для отправки запроса.")
    elif text == "Калькулятор":
        kb = InlineKeyboardBuilder()
        kb.button(text="Сложение ➕", callback_data="add")
        kb.button(text="Вычитание ➖", callback_data="sub")
        kb.button(text="Умножение ✖️", callback_data="mul")
        kb.button(text="Деление ➗", callback_data="div")
        kb.adjust(2)
        await message.answer("Выбери операцию:", reply_markup=kb.as_markup())
    else:
        await message.answer("Пожалуйста, выбери действие из меню.", reply_markup=keyboard)

@dp.callback_query()
async def process_operation(callback: types.CallbackQuery):
    data = callback.data
    if data not in ("add", "sub", "mul", "div"):
        await callback.answer("Неизвестная операция.", show_alert=True)
        return
    user_id = callback.from_user.id
    user_op[user_id] = data
    waiting_for_numbers.add(user_id)
    await callback.message.answer("Введи два числа через пробел, например: 5 3")
    await callback.answer()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
