from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
import asyncio
import os
import subprocess
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from langchain_community.vectorstores import Chroma

from upload_state import UploadState
from request_state import RequestState
from notion_worker import NotionWorker
from langchain_community.embeddings.yandex import YandexGPTEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from rag_handiling import handle_query


from settings import API_TOKEN, Ya_API_KEY, FOLDER_ID


bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_vectorstores = {}

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
    question = message.text
    user_id = message.chat.id

    answer = await handle_query(user_id, user_vectorstores, question)

    await message.reply(f"Ответ: {answer}")
    await state.clear()


@dp.message(StateFilter(UploadState.waiting_for_notion_link))
async def handle_notion_link(message: types.Message, state: FSMContext):
    notion_link = message.text
    user_id = message.chat.id

    token = NotionWorker.extract_token_from_url(notion_link)

    worker = NotionWorker()
    worker.parse_page_content(token)
    content = worker.result

    # content = ["Спокойный (эсминец)\nЗачислен в списки ВМФ СССР 19 августа 1952 года.",
    #            "Спокойный (эсминец)\nЗачислен в списки ВМФ СССР 19 августа 1952 года.",
    #            "Спокойный (эсминец)\nЗачислен в списки ВМФ СССР 19 августа 1952 года.",
    #            "Спокойный (эсминец)\nЗачислен в списки ВМФ СССР 19 августа 1952 года."]

    model = YandexGPTEmbeddings(api_key=Ya_API_KEY, folder_id=FOLDER_ID)
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300,
        chunk_overlap=100)
    documents = [Document(page_content=text) for text in content]
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(documents=splits, embedding=model)

    user_vectorstores[user_id] = vectorstore

    print(content)
    await message.reply(f"Notion успешно подключен")
    await state.clear()


dp.message.register(send_welcome, F.text == "Помощь")
dp.message.register(request_notion_link, F.text == "Подключить Notion")
dp.message.register(request_query_text, F.text == "Задать вопрос к Notion")

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
