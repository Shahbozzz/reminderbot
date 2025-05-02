🤖 Telegram Reminder Bot with AI Text Improvement

This is a Telegram bot built with [aiogram](https://github.com/aiogram/aiogram), OpenAI GPT, and PostgreSQL. It allows users to:
- Set up to 3 reminders with associated dates
- Improve the quality of short text messages using OpenAI
- Automatically store user data and language preferences

📦 Features

- ✅ Multilingual support (e.g., English, Russian)
- ✅ Reminder creation (up to 3 per user)
- ✅ GPT-3.5-powered text refinement
- ✅ PostgreSQL-based user data storage
- ✅ Environment-based secret management

🚀 Installation

1. Clone the repository

```bash
git clone https://github.com/Shahbozzz/reminderbot.git
cd reminderbot
Install dependencies

bash
pip install -r requirements.txt
Set up environment variables

Create a .env file in the root directory:

env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_key
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_NAME=your_database
DB_HOST=localhost
Create the PostgreSQL database

Make sure your database has the following tables:

sql
CREATE TABLE clients (
    telegram_id BIGINT PRIMARY KEY,
    fullname TEXT,
    username TEXT,
    user_language TEXT
);

CREATE TABLE reminders (
    telegram_id BIGINT PRIMARY KEY,
    text1 TEXT,
    text2 TEXT,
    text3 TEXT,
    date1 DATE,
    date2 DATE,
    date3 DATE
);

🧠 How it works
When a user sends a message, the bot saves their profile info.

Users can send short texts to be improved via OpenAI.

Each user can set up to 3 reminders with corresponding dates.

All data is stored in PostgreSQL.

🛠️ Tech Stack
Python 3.10+

aiogram for Telegram bot framework

asyncpg for PostgreSQL access

OpenAI GPT-3.5 API

dotenv for environment variable management


🧑‍💻 Author
Shohboz – @k2_bodyguard(Telegram)
