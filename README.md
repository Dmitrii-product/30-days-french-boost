# Daily French Boost Telegram Bot

A Telegram bot designed to daily send French learners 1 vocabulary word appropriate for their selected CEFR level (A1 - C2), along with its definition and an example sentence. Also includes a Golden List mechanism for spaced repetition.

## Architecture
- Database: Supabase / PostgreSQL
- Orchestrator: `python-telegram-bot`
- Deployment: Render.com Web Service
- Security: Uses `cryptography.fernet` to symmetric-encrypt Telegram Chat IDs.

## Requirements
- Python 3.9+
- A Supabase Project
- A Telegram Bot Token from BotFather

## `.env` Configuration
You need to set up the following environment variables:
```
TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ENCRYPTION_KEY=your_fernet_encryption_key
```
Note: You can generate an encryption key by running:
`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## Local Setup
1. Create virtual environment: `python3 -m venv .venv` and activate it.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the bot: `python bot.py`
