import openai
from aiogram.handlers import message

from database.crud import create_db_connection
from database.crud import get_user_language

import os
openai.api_key = os.getenv('OPENAI_API_KEY')

# Функция генерации улучшенного текста
async def improve_text(original_text: str) -> str:
    conn = await create_db_connection()
    lang = await get_user_language(conn, message.from_user.id)
    prompt = f"Сохраняя смысл и число слов, сгенерируй этот текст более красивым и объяснимым на : {original_text}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,  # Ограничиваем количество токенов
        temperature=0.7
    )

    improved_text = response.choices[0].message.content.strip()

    # Ограничиваем результат до 10 слов
    improved_words = improved_text.split()[:10]  # Берем первые 10 слов
    return ' '.join(improved_words)  # Возвращаем строку с 10 словами
