import json
import openai
from aiogram import Router, F, types,Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import datetime
from datetime import datetime, date
from asyncpg import Connection
import asyncio
from keyboards.for_inline_keyboards import user_lang,delete_reminder,reminder_month,get_date_keyboard
from database.crud import (
    create_db_connection, save_user, get_user_language,
    save_reminder, count_user_reminders,save_date
)
from keyboards.for_keyboards import main_buttons

import os
openai.api_key = os.getenv('OPENAI_API_KEY')

router = Router()

#Uploading json language files
with open("locales/en.json", "r", encoding="utf-8") as f:
    en = json.load(f)
with open("locales/ru.json", "r", encoding="utf-8") as f:
    ru = json.load(f)
with open("locales/uz.json", "r", encoding="utf-8") as f:
    uz = json.load(f)
#Uploading json language files


locales = {"en": en, "ru": ru, "uz": uz} #Saving it in dictionary


#Start bot
@router.message(Command("start"))
async def start(message:Message):
    await message.answer(
        locales['en']['start'],
        reply_markup=user_lang()
    )
#Start bot


#Changing language
@router.message(Command("lang"))
async def change_lang(message:Message):
    conn=await create_db_connection()
    lang=await get_user_language(conn, message.from_user.id)
    await message.answer(
        locales[lang]["start"],
        reply_markup=user_lang()
    )
    await conn.close()
#Changing language


#Saving language of user while changing
@router.callback_query(lambda c: c.data.startswith("lang_"))
async def process_lang(callback: CallbackQuery):
    conn = await create_db_connection()
    lang = callback.data.split('_')[1]
    await save_user(conn, callback.from_user.id, callback.from_user.full_name, callback.from_user.username, lang)
    buttons = await main_buttons(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(locales[lang]['choose_actions'], reply_markup=buttons)
    await callback.answer()
    await conn.close()
#Saving language of user while changing

#Send remindeers if user asked to do so
@router.message(F.text.lower().in_(["мои события", "my actions to remind", "mening eslatmalarim"]))
async def my_reminders(message: Message):
    conn = await create_db_connection()
    lang = await get_user_language(conn, message.from_user.id)

    reminders = await conn.fetchrow(  # fetchrow() вернёт 1 объект (словарь)
        "SELECT text1, date1, text2, date2, text3, date3 FROM reminders WHERE telegram_id = $1",
        message.from_user.id
    )

    if not reminders or all(value is None for value in reminders.values()):
        # Check if reminders is None or all values in the dictionary are None
        await message.answer(locales[lang]['no_reminders'])  # Если записей нет
    else:
        for i in range(1, 4):  # Перебираем 1, 2, 3
            text = reminders[f"text{i}"]  # Получаем текст напоминания
            date = reminders[f"date{i}"]  # Получаем дату напоминания

            if text:  # Если есть текст, отправляем
                formatted_date = date.strftime("%d-%m-%Y") if date else "❌"  # Форматируем дату
                reminder_text = f"{text} \n\n📅 {formatted_date}"  # Формируем текст с датой
                keyboard = await delete_reminder(conn, message.from_user.id, text, i)  # Клавиатура удаления
                await message.reply(reminder_text, reply_markup=keyboard)  # Отправляем напоминание

    await conn.close()



#Sending reminders after saving
async def send_reminders(bot: Bot, conn: Connection):
    while True:
        now = date.today()  # Текущая дата (без времени)

        reminders = await conn.fetch(
            "SELECT telegram_id, text1, date1, text2, date2, text3, date3 FROM reminders"
        )

        for row in reminders:
            tg_id = row["telegram_id"]
            for i in range(1, 4):  # Перебираем все 3 напоминания
                text = row[f"text{i}"]
                event_date = row[f"date{i}"]

                if text and event_date:
                    # Если event_date является datetime, приводим к date
                    if hasattr(event_date, "date"):
                        event_date = event_date.date()

                    days_left = (event_date - now).days  # Вычисляем оставшиеся дни

                    # Если осталось более 3 дней и число дней делится на 3 (каждые 3 дня)
                    if days_left > 3 and days_left % 3 == 0:
                        await bot.send_message(
                            tg_id,
                            f"📌 Напоминание:\n{text}\n\n⏳ Осталось {days_left} дней!"
                        )
                    # Если до события осталось 3 или менее дней, отправляем напоминание ежедневно
                    elif 0 < days_left <= 3:
                        await bot.send_message(
                            tg_id,
                            f"⚠️ Warning! To the action {text} {days_left} day left:)"
                        )
                    # В день события отправляем уведомление и удаляем напоминание
                    elif days_left == 0:
                        await bot.send_message(
                            tg_id,
                            f"✅ Сегодня день события:\n{text}\n\n❌ Напоминание удалено."
                        )
                        await conn.execute(
                            f"UPDATE reminders SET text{i} = NULL, date{i} = NULL WHERE telegram_id = $1",
                            tg_id
                        )
        # Приостанавливаем выполнение на 24 часа (86400 секунд)
        await asyncio.sleep(30)
#Sending reminders after saving


#Delete reminder if user send callback to do so
@router.callback_query(lambda c: c.data.startswith("delete_reminder_"))
async def delete_reminders(callback: CallbackQuery):
    conn = await create_db_connection()
    lang = await get_user_language(conn, callback.from_user.id)
    reminder_index = int(callback.data.split('_')[2])  # Получаем 1, 2 или 3
    telegram_id = callback.from_user.id

    if reminder_index in (1, 2, 3):  # Проверяем, что индекс корректный
        text_column = f"text{reminder_index}"  # text1, text2 или text3
        date_column = f"date{reminder_index}"  # date1, date2 или date3

        # Обнуляем textX и dateX
        await conn.execute(
            f"UPDATE reminders SET {text_column} = NULL, {date_column} = NULL WHERE telegram_id = $1",
            telegram_id
        )

        await callback.message.edit_text(locales[lang]["reminder_deleted"])  # Меняем текст
    else:
        await callback.message.answer(locales[lang]['alert_error'])

    await callback.answer()
    await conn.close()
#Delete reminder if user send callback to do so


#Improved reminder
async def improve_feedback(text):
    prompt = f"Событие для напоминания:{text} . Проанализируй его и дай рекомендации. Текст будет соьытие которое произойдет с ним или т.д. Ты должен дать конкретный совет,чтоб эти советы он мог использовать в будущем когда это событие произойдёт Дай текст на языке который был  написан текст"

    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,  # Set max tokens
        temperature=0.7
    )
    improved_text = response['choices'][0]['message']['content'].strip()
    return improved_text
#Improved reminder


#Get feedback text
@router.callback_query(lambda a: a.data.startswith("feedback_"))
async def get_text(callback: CallbackQuery):
    conn = await create_db_connection()
    feedback_index=int(callback.data.split('_')[1])
    text_column = f"text{feedback_index}"
    telegram_id = callback.from_user.id
    text = await conn.fetchval(
        f"SELECT {text_column} FROM reminders WHERE telegram_id = $1  ",telegram_id
    )
    improved_feedback = await improve_feedback(text)
    await callback.message.answer(improved_feedback)
    await conn.close()

#Get feedback text



#Saving month of reminder
@router.callback_query(lambda c: c.data.startswith("month_"))
async def reply_date(callback: types.CallbackQuery):
    conn = await create_db_connection()
    lang = await get_user_language(conn, callback.from_user.id)

    selected_month = callback.data.split("_")[1]
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"{locales[lang]['choose_date']}",
        reply_markup=get_date_keyboard(selected_month)
    )
    await callback.message.delete()
    await callback.answer()
#Saving month of reminder


#Saving date of reminder
@router.callback_query(lambda c: c.data.startswith("date_"))
async def save_data(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    conn = await create_db_connection()
    lang = await get_user_language(conn, telegram_id)

    _, month, day = callback.data.split("_")
    month_number = datetime.strptime(month, "%B").month
    chosen_date = date(date.today().year, month_number, int(day))  # Преобразуем в date

    # Проверяем, не является ли дата прошедшей
    if chosen_date <= date.today():
        await callback.message.answer(locales[lang]["invalid_date"])  # Показываем предупреждение
        await callback.message.delete()  # Убираем кнопки
        await callback.message.answer(
            locales[lang]["choose_month"], reply_markup=await reminder_month(conn,telegram_id)
        )  # Отправляем клавиатуру с выбором месяца
        return  # Выходим из функции

    # Если дата корректна, сохраняем
    await save_date(conn, telegram_id, chosen_date)
    await callback.message.edit_text(locales[lang]['reminder_saved'])
    await callback.answer()
#Saving date of reminder


#Adding reminder
user_states = {} #Temporary storage of user condition
@router.message(F.text.lower().in_(["add action to remind", "добавить событие", "eslatma qo'shish"]))
async def reminder(message: Message):
    telegram_id=message.from_user.id
    """ Проверяет, можно ли добавить напоминание, и запрашивает текст """
    conn = await create_db_connection()
    lang = await get_user_language(conn, telegram_id)
    reminder_count = await count_user_reminders(conn, telegram_id)

    if reminder_count >= 3:
        await message.answer(locales[lang]["max_reminder"])  # <-- ДОБАВЛЕНО: Сообщение о лимите
        await conn.close()
        return

    user_states[message.from_user.id] = "waiting_for_reminder"
    await message.answer(locales[lang]["send_message"])
    await conn.close()
#Adding reminder


#Improved reminder
async def improve_text(message: types.Message, original_text: str) -> str:
    conn = await create_db_connection()
    lang = await get_user_language(conn, message.from_user.id)
    prompt = f"Это событие который user попросил напоминать что у него это событие будет!Сохраняя смысл и число слов без лишних слов, сгенерируй этот текст более красивым и объяснимым на {lang} языке: {original_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,  # Ограничиваем количество токенов
        temperature=0.7
    )

    improved_text = response['choices'][0]['message']['content'].strip()

    # Ограничиваем результат до 10 слов
    improved_words = improved_text.split()[:10]  # Берем первые 10 слов
    return ' '.join(improved_words)  # Возвращаем строку с 10 словами
#Improved reminder


# Save user reminder after user sends it
@router.message()
async def save_user_reminder(message: Message):
    """ Сохраняет напоминание, если пользователь в нужном состоянии и не превысил лимит """

    conn = await create_db_connection()
    lang = await get_user_language(conn, message.from_user.id)

    if message.from_user.id in user_states and user_states[message.from_user.id] == "waiting_for_reminder":
        if len(message.text) > 70:
            await message.answer(locales[lang]["urgent_reminder"])
            await conn.close()
            return

        # Передаем сообщение в improve_text
        improved_reminder = await improve_text(message, message.text)

        success = await save_reminder(conn, message.from_user.id, improved_reminder)

        if success:
            await message.answer(locales[lang]['choose_month'],
                                 reply_markup=await reminder_month(conn, message.from_user.id))

        else:
            await message.answer(locales[lang]["max_reminder"])  # <-- Теперь бот сообщает о лимите

        await conn.close()
        del user_states[message.from_user.id]
