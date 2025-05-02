import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from handlers import questions, different_types
from database.crud import create_db_connection  # Подключение к БД
from handlers.questions import send_reminders  # Функция для напоминаний
from dotenv import load_dotenv

async def main():
    load_dotenv()  # Load environment variables from .env file
    bot_token = os.getenv("BOT_TOKEN")  # Get token from environment variable

    if not bot_token:
        raise ValueError("No bot token found in the .env file")

    bot = Bot(token=bot_token,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML
              ))

    dp = Dispatcher()
    dp.include_routers(questions.router, different_types.router)

    conn = await create_db_connection()  # Подключаемся к БД

    # Запускаем фоновую задачу
    asyncio.create_task(send_reminders(bot, conn))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
