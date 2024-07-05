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

from settings import Ya_API_KEY, FOLDER_ID


def create_db_connection():
    try:
        connection = psycopg2.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error: {e}")
        return None


def upload_message_to_db(user_id, message, response=None):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        current_time = int(time.time())  # Get the current time as UNIX timestamp
        insert_query = """
        INSERT INTO requests (user_id, query, response, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, message, response, current_time))
        connection.commit()
        cursor.close()
        connection.close()


def fetch_last_queries_and_responses(user_id):
    connection = create_db_connection()
    if connection:
        cursor = connection.cursor()
        select_query = """
        SELECT query, response FROM requests
        WHERE user_id = %s
        ORDER BY timestamp DESC
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
def create_prompt(queries, responses):
    # Создаем историю сообщений в виде строки
    history = "\n".join([f"Пользователь: {query}\nСистема: {response}" for query, response in zip(queries, responses)])

    # Вводный промт
    intro_template = (
        "Эта система является экспертом в области обработки данных, способным анализировать и интерпретировать "
        "информацию на основе истории сообщений и контекста. Пожалуйста, предоставьте детальные и точные ответы, "
        "используя предоставленные данные. Не задавай уточняющих вопросов. Твой ответ должен быть конечным.\n"
        "Контекст: {context}\n"
        "Вопрос: {question}\n"
        "История сообщений:\n")

    # Объединяем вводный промт и историю сообщений
    full_template = intro_template + history

    prompt = ChatPromptTemplate.from_template(full_template)

    return prompt


async def handle_query(user_id, user_vectorstores, question):
    if user_id in user_vectorstores:
        vectorstore = user_vectorstores[user_id]
        retriever = vectorstore.as_retriever()
        q, r = fetch_last_queries_and_responses(user_id)

        llm = YandexGPT(api_key=Ya_API_KEY, folder_id=FOLDER_ID, model_name='yandexgpt')
        print(llm.model_name)

        prompt = create_prompt(q, r)

        rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
        )

        llm_response = rag_chain.invoke(question)
        upload_message_to_db(user_id, question, llm_response)

        return llm_response
    else:
        return "Сначала подключите Notion с помощью команды 'Подключить Notion'."
