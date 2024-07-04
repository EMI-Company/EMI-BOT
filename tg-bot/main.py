from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode  # измененный импорт
import asyncio
from aiogram.filters import Command  # новый импорт для фильтра команд

API_TOKEN = '7428709784:AAHybBmsbItOZJ6drhk3ALdTWAvrvBgme1c'
NOTION_API_KEY = 'secret_pvaGGjmtgix2XU8MlKJpFoAUEjUgiR6CNW7s5av7FCI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=['start', 'help']))  # исправленный декоратор
async def send_welcome(message: types.Message):
    button = types.KeyboardButton(text="Подключить Notion")
    markup = types.ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True, selective=True)

    greeting_message = ("Привет! Я ваш бот для Notion, который позволяет вам напрямую общаться с вашими документами. " +
                        "Задайте мне вопрос, и я найду для вас нужную информацию.")


    await message.answer(greeting_message, reply_markup=markup)

@dp.message()
async def handle_query(message: types.Message):
    query = message.text

    await message.reply("хуй", parse_mode=ParseMode.MARKDOWN)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
