from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode  # измененный импорт
import asyncio
from aiogram.filters import Command  # новый импорт для фильтра команд


API_TOKEN = '7450850829:AAH7YKXTeihzOmaiG0c-RWAN2gcSPfQAwtc'
NOTION_API_KEY = 'secret_pvaGGjmtgix2XU8MlKJpFoAUEjUgiR6CNW7s5av7FCI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command(commands=['start', 'help']))  # исправленный декоратор
async def send_welcome(message: types.Message):
    await message.reply("Hello! I am your Notion RAG bot. Send me a query and I'll fetch the information from your Notion documents.")


@dp.message()
async def handle_query(message: types.Message):
    query = message.text

    await message.reply("хуй", parse_mode=ParseMode.MARKDOWN)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
