from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.crud import get_user_language,create_db_connection
import json


# Open json files from locales directory
with open("locales/en.json", "r", encoding="utf-8") as f:
    en = json.load(f)
with open("locales/ru.json", "r", encoding="utf-8") as f:
    ru = json.load(f)
with open("locales/uz.json", "r", encoding="utf-8") as f:
    uz = json.load(f)

locales = {
    "en": en,
    "ru": ru,
    "uz": uz
}

async def main_buttons(user_id):
    conn = await create_db_connection()
    lang = await get_user_language(conn, user_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=locales[lang]['add_action'])],
            [KeyboardButton(text=locales[lang]['added_action'])]
        ],
        resize_keyboard=True
    )

    return keyboard
