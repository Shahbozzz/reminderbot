import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env
async def create_db_connection():
    return await asyncpg.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST")
)
async def return_clients(conn):
    return await conn.fetch("SELECT * FROM client")

async def save_user(conn, telegram_id, fullname, username, lang):
    """ Сохраняет или обновляет пользователя в базе данных """
    user = await conn.fetchrow("SELECT * FROM clients WHERE telegram_id =$1", telegram_id)


    if user:
        await conn.execute('''
        UPDATE clients
        SET fullname=$1, username=$2, user_language=$3
        WHERE telegram_id=$4
        ''', fullname, username,lang, telegram_id
        )
    else:
        await conn.execute('''
            INSERT INTO clients (telegram_id, fullname,username,user_language)
            VALUES ($1, $2, $3, $4)
        ''', telegram_id, fullname, username, lang
        )

async def get_user_language(conn, telegram_id):
    """ Получает язык пользователя из базы данных """
    user = await conn.fetchrow('SELECT user_language FROM clients WHERE telegram_id = $1', telegram_id)
    return user['user_language'] if user else 'en'  # По умолчанию 'en', если нет в базе


async def count_user_reminders(conn, telegram_id):
    """ Считает количество напоминаний пользователя """
    count = await conn.fetchval('SELECT COUNT(*) FROM reminders WHERE telegram_id = $1', telegram_id)
    return count


from datetime import datetime
async def save_date(conn, telegram_id, date_obj):  # Параметр уже date
    date_reminder = await conn.fetchrow(
        'SELECT date1, date2, date3 FROM reminders WHERE telegram_id = $1',
        telegram_id
    )

    if not date_reminder:
        # Если у пользователя нет записей, создаем новую
        await conn.execute(
            'INSERT INTO reminders (telegram_id, date1) VALUES ($1, $2)',
            telegram_id, date_obj
        )
    else:
        # Ищем первую свободную дату
        if date_reminder['date1'] is None:
            column = 'date1'
        elif date_reminder['date2'] is None:
            column = 'date2'
        elif date_reminder['date3'] is None:
            column = 'date3'
        else:
            return False  # Все даты заняты, ничего не делаем

        # Обновляем первую свободную колонку
        await conn.execute(
            f'UPDATE reminders SET {column} = $1 WHERE telegram_id = $2',
            date_obj, telegram_id
        )

    return True

async def save_reminder(conn, telegram_id, text):
    """ Сохраняет напоминание в один из трех слотов text1, text2 или text3 """

    reminder = await conn.fetchrow('SELECT text1, text2, text3 FROM reminders WHERE telegram_id = $1', telegram_id)

    if not reminder:
        # Если у пользователя еще нет записей, создаем новую строку
        await conn.execute('''
            INSERT INTO reminders (telegram_id, text1)
            VALUES ($1, $2)
        ''', telegram_id, text)

    elif reminder['text1'] is None:
        await conn.execute('''
            UPDATE reminders SET text1 = $1 WHERE telegram_id = $2
        ''', text, telegram_id)

    elif reminder['text2'] is None:
        await conn.execute('''
            UPDATE reminders SET text2 = $1 WHERE telegram_id = $2
        ''', text, telegram_id)

    elif reminder['text3'] is None:
        await conn.execute('''
            UPDATE reminders SET text3 = $1 WHERE telegram_id = $2
        ''', text, telegram_id)

    else:
        return False  # Уже три напоминания, нельзя добавлять новые

    return True  # Напоминание успешно сохранено

async def get_lang(conn, telegram_id):
    conn = await create_db_connection()
    lang = await get_user_language(conn, telegram_id)
    await conn.close()
    return lang