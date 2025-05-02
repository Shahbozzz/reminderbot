from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

def user_lang():
    builder=InlineKeyboardBuilder()
    builder.button(text="🇺🇸 English", callback_data="lang_en")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    builder.adjust(3)
    return builder.as_markup()


async def delete_reminder(conn,telegram_id, reminder_text, index):
    lang = await get_user_language(conn, telegram_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"🗑 {locales[lang]["delete_reminder"]}",
        callback_data=f"delete_reminder_{index}"
    )
    builder.button(
        text=f"✨{locales[lang]["feedback"]}",
        callback_data=f"feedback_{index}"
    )
    return builder.as_markup()

async def reminder_month(conn,telegram_id) -> InlineKeyboardMarkup:
    lang = await get_user_language(conn, telegram_id)
    inline_keyboard =InlineKeyboardBuilder()
    months=locales[lang]['month']
    for i,month in enumerate(months):
        inline_keyboard.add(InlineKeyboardButton(
            text=str(month),
            callback_data=f"month_{locales['en']['month'][i]}"
        ))
    inline_keyboard.adjust(3)
    return inline_keyboard.as_markup(one_time_keyboard=True,resize_keyboard=True)

MONTH_DAYS = {
    'January': 31,
    "February": 28,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31,
}

def get_date_keyboard(month: str)-> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    days = MONTH_DAYS[month]
    for day in range(1, days + 1):
        builder.button(text=str(day),callback_data=f"date_{month}_{day}")
    builder.adjust(7)
    return builder.as_markup()
