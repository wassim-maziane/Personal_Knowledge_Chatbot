import psycopg2
from psycopg2.extras import DictCursor

DB_NAME = "app"
DB_USER = "root"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    return conn


def create_chat_logs_table():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """ CREATE TABLE IF NOT EXISTS chat_logs (
                                id SERIAL PRIMARY KEY,
                                session_id TEXT,
                                user_query TEXT,
                                gpt_response TEXT,
                                model TEXT,
                                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP)
                                """
            )
        conn.commit()
    finally:
        conn.close()


def insert_chat_log(session_id, user_query, gpt_response, model):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO chat_logs (session_id, user_query, gpt_response, model) VALUES (%s, %s, %s, %s)
        """,
            (session_id, user_query, gpt_response, model),
        )
    conn.commit()
    conn.close()


def get_chat_history(session_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            """ SELECT user_query, gpt_response FROM chat_logs WHERE session_id = %s ORDER BY created_at """,
            (session_id,),
        )
        messages = []
        rows = cursor.fetchall()
        for row in rows:
            messages.extend(
                [
                    {"role": "human", "content": row["user_query"]},
                    {"role": "ai", "content": row["gpt_response"]},
                ]
            )
    conn.close()
    return messages


create_chat_logs_table()

# def create_document_store():
#     conn = get_db_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS document_store(
#                 id SERIAL PRIMARY_KEY,
#                 filename TEXT,
#                 uploaded_at TIMESTAMPZ DEFAULT CURRENT_TIMESTAMP
#             )
#         """
#         )
#     conn.close()
