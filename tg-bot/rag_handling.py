import psycopg2
from langchain.prompts import ChatPromptTemplate
import time
from aiogram import types
from langchain_community.llms import YandexGPT
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

db_config = {
    'dbname': 'emi',
    'user': 'emi',
    'password': 'password',
    'host': '194.87.186.59',
    'port': '5433',
}


async def create_db_connection():
    try:
        connection = psycopg2.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None


async def upload_message_to_db(user_id, message, response=None):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        current_time = int(time.time())  # Get the current time as UNIX timestamp
        insert_query = """
        INSERT INTO user_interactions (user_id, message, response, created_at)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, message, response, current_time))
        connection.commit()
        cursor.close()
        connection.close()


async def fetch_last_queries_and_responses(user_id):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        select_query = """
        SELECT message, response FROM user_interactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 20
        """
        cursor.execute(select_query, (user_id,))
        results = cursor.fetchall()
        queries = [row[0] for row in results if row[0] is not None]
        responses = [row[1] for row in results if row[1] is not None]
        cursor.close()
        connection.close()
        return queries[:10], responses[:10]


# Function to create the JSON prompt
async def create_prompt(queries, responses):
    # Создаем историю сообщений в виде строки
    history = "\n".join([f"Пользователь: {query}\nСистема: {response}" for query, response in zip(queries, responses)])

    # Вводный промт
    intro_template = (
        "Эта система является экспертом в области обработки данных. Она должна опираться в своём ответе на историю сообщений и контекст.\n"
        "Контекст: {context}\n"
        "Вопрос: {question}\n"
        "История сообщений:\n")

    # Объединяем вводный промт и историю сообщений
    full_template = intro_template + history

    prompt = ChatPromptTemplate.from_template(full_template)

    return prompt


async def handle_query(user_id, user_vectorstores, question):
    API_KEY = "AQVNwz7kWZJVwzfzkkIgABYm9WZhZ7PVdbAEz45i"
    FOLDER_ID = "b1goe5po366bkpcovo87"

    if user_id in user_vectorstores:
        vectorstore = user_vectorstores[user_id]
        retriever = vectorstore.as_retriever()
        q, r = fetch_last_queries_and_responses(user_id)

        llm = YandexGPT(api_key=API_KEY, folder_id=FOLDER_ID)

        prompt = create_prompt(q, r)

        rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
        )

        results = retriever.retrieve(question)

        return rag_chain.invoke("Кто живёт на Марсе?")
    else:
        return "Сначала подключите Notion с помощью команды 'Подключить Notion'."
