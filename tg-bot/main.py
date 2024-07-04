# from aiogram import Bot, Dispatcher, types, F
# from aiogram.enums import ParseMode  # измененный импорт
# import asyncio
# from aiogram.filters import Command, StateFilter  # новый импорт для фильтра команд
# from aiogram.fsm.context import FSMContext
# from upload_state import UploadState
#
# API_TOKEN = '7428709784:AAHybBmsbItOZJ6drhk3ALdTWAvrvBgme1c'
# NOTION_API_KEY = 'secret_pvaGGjmtgix2XU8MlKJpFoAUEjUgiR6CNW7s5av7FCI'
#
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()
#
#
# @dp.message(Command(commands=['start', 'help']))  # исправленный декоратор
# async def send_welcome(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(
#         keyboard=[
#             [types.KeyboardButton(text="Помощь")],
#             [types.KeyboardButton(text="Подключить Notion")],
#             [types.KeyboardButton(text="Задать вопрос к Notion")]
#         ],
#         resize_keyboard=True
#     )
#
#     greeting_message = (
#                 "Привет! \n Я ваш бот для Notion, который позволяет вам напрямую общаться с вашими документами. " +
#                 "Задайте мне вопрос, и я найду для вас нужную информацию.\n \n" +
#                 "Список моих команд: \n1. Помощь - вывести список команд \n2. Подключить Notion - загрузить исходные данные Notion \n3. Задать вопрос к Notion - задать вопрос на основе Notion")
#
#     await message.answer(greeting_message, reply_markup=keyboard)
#
#
# async def request_notion_link(message: types.Message, state: FSMContext):
#     await message.reply("Введите ссылку на родительскую страницу требуемых документов")
#     await state.set_state(UploadState.waiting_for_notion_link)
#
#
# @dp.message(StateFilter(UploadState.waiting_for_notion_link))
# async def handle_notion_link(message: types.Message, state: FSMContext):
#     notion_link = message.text
#     # Здесь вы можете обработать полученную ссылку на Notion
#     await message.reply(f"Got the Notion link: {notion_link}")
#     await state.clear()
#
# async def request_question(message: types.Message, state: FSMContext):
#     await message.reply("Введите ваш запрос")
#     await state.set_state(UploadState.waiting_for_notion_link)
#
#
# dp.message.register(send_welcome, F.text == "Помощь")
# dp.message.register(request_notion_link, F.text == "Подключить Notion")
# dp.message.register(request_question, F.text == "Задать вопрос к Notion")
#
# async def main():
#     await dp.start_polling(bot)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
import asyncio
import os
import subprocess
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from upload_state import UploadState
from request_state import RequestState
from notion_worker import NotionWorker

from settings import API_TOKEN


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command(commands=['start', 'help']))  # исправленный декоратор
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Помощь")],
            [types.KeyboardButton(text="Подключить Notion")],
            [types.KeyboardButton(text="Задать вопрос к Notion")]
        ],
        resize_keyboard=True

    )

    greeting_message = (
        "Привет! \n Я ваш бот для Notion, который позволяет вам напрямую общаться с вашими документами. " +
        "Задайте мне вопрос, и я найду для вас нужную информацию.\n \n" +
        "Список моих команд: \n1. Помощь - вывести список команд \n2. Подключить Notion - загрузить исходные данные Notion \n3. Задать вопрос к Notion - задать вопрос на основе Notion")

    await message.answer(greeting_message, reply_markup=keyboard)


async def request_notion_link(message: types.Message, state: FSMContext):
    await message.reply("Введите ссылку на родительскую страницу требуемых документов")
    await state.set_state(UploadState.waiting_for_notion_link)


async def request_query_text(message: types.Message, state: FSMContext):
    await message.reply("Введите формулировку запроса")
    await state.set_state(RequestState.waiting_for_request_text)


@dp.message(StateFilter(RequestState.waiting_for_request_text))
async def handle_request_text(message: types.Message, state: FSMContext):
    text = message.text

    await message.reply(f"Got request text: {text}")
    await state.clear()


@dp.message(StateFilter(UploadState.waiting_for_notion_link))
async def handle_notion_link(message: types.Message, state: FSMContext):
    notion_link = message.text
    token = NotionWorker.extract_token_from_url(notion_link)

    worker = NotionWorker()
    worker.parse_page_content(token)
    content = worker.result

    print(content)
    await message.reply(f"Got the Notion link: {notion_link}")
    await state.clear()


dp.message.register(send_welcome, F.text == "Помощь")
dp.message.register(request_notion_link, F.text == "Подключить Notion")
dp.message.register(request_query_text, F.text == "Задать вопрос к Notion")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
