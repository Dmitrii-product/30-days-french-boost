import json
import random
import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import Conflict
import db
from dotenv import load_dotenv
import threading
from flask import Flask

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web_server():
    port = int(os.environ.get('PORT', 5000))
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv('TOKEN')
if not TOKEN:
    print("Warning: TOKEN environment variable not set.")

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    db.add_or_update_user(user_id, "C1") # Default to C1
    
    keyboard = [
        [InlineKeyboardButton(lvl, callback_data=f"level_{lvl}") for lvl in LEVELS[:3]],
        [InlineKeyboardButton(lvl, callback_data=f"level_{lvl}") for lvl in LEVELS[3:]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Welcome to the Daily French Boost Bot!\n\n"
        "I'll send you a new French word every day.\n"
        "Please select your target French level below:",
        reply_markup=reply_markup
    )

async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    current_level = db.get_user_level(user_id) or "Not set"
    
    keyboard = [
        [InlineKeyboardButton(lvl, callback_data=f"level_{lvl}") for lvl in LEVELS[:3]],
        [InlineKeyboardButton(lvl, callback_data=f"level_{lvl}") for lvl in LEVELS[3:]]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Your current level is: *{current_level}*\n\n"
        "Choose a new level:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_single_word(context: ContextTypes.DEFAULT_TYPE, chat_id: int, level: str):
    with open('words.json', 'r', encoding='utf-8') as f:
        all_words = json.load(f)
    level_words = [w for w in all_words if w.get('level') == level]
    if not level_words:
        return
    entry = random.choice(level_words)
    message = (
        f"🌟 *{level} French Word of the Day: {entry['word']}*\n\n"
        f"📚 *Translation / Definition:* {entry['definition']}\n\n"
        f"📝 *Example:* _{entry['example']}_\n\n"
    )
    if "see_also" in entry and entry["see_also"]:
        message += f"🔗 *See Also:* {', '.join(entry['see_also'])}\n\n"
        
    message += (
        f"--- \n"
        f"💪 *Stress Test:* Can you use '{entry['word'].lower()}' in a sentence today?"
    )
    bot_username = context.bot.username
    keyboard = [[InlineKeyboardButton("🤖 View Bot", url=f"https://t.me/{bot_username}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        db.add_word_to_vocabulary(chat_id, entry['word'])
        await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        print(f"Failed to send to {chat_id}: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("level_"):
        new_level = data.split("_")[1]
        user_id = update.effective_chat.id
        db.add_or_update_user(user_id, new_level)
        await query.edit_message_text(f"✅ Your level has been updated to *{new_level}*!\nYou'll receive words for this level daily.", parse_mode='Markdown')
        await send_single_word(context, user_id, new_level)
    elif data.startswith("vocab_"):
        word = data.split("_", 1)[1]
        user_id = update.effective_chat.id
        current_status = db.get_word_status(user_id, word)
        
        if current_status is not None:
            new_status = not current_status
            db.update_word_status(user_id, word, new_status)
            
            new_keyboard = []
            for row in update.callback_query.message.reply_markup.inline_keyboard:
                new_row = []
                for button in row:
                    if button.callback_data == data:
                        new_text = f"✅ {word}" if new_status else f"❌ {word}"
                        new_row.append(InlineKeyboardButton(new_text, callback_data=data))
                    else:
                        new_row.append(button)
                new_keyboard.append(new_row)
                
            try:
                await update.callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))
            except Exception as e:
                print(f"Failed to update golden list keyboard: {e}")

async def send_daily_words(context: ContextTypes.DEFAULT_TYPE):
    with open('words.json', 'r', encoding='utf-8') as f:
        all_words = json.load(f)
    
    users = db.get_all_users()
    if not users:
        return
    
    users_by_level = {lvl: [] for lvl in LEVELS}
    for chat_id, level in users:
        if level in users_by_level:
            users_by_level[level].append(chat_id)
            
    for level, chat_ids in users_by_level.items():
        if not chat_ids:
            continue
            
        level_words = [w for w in all_words if w.get('level') == level]
        if not level_words:
            continue
            
        entry = random.choice(level_words)
        message = (
            f"🌟 *{level} French Word of the Day: {entry['word']}*\n\n"
            f"📚 *Translation / Definition:* {entry['definition']}\n\n"
            f"📝 *Example:* _{entry['example']}_\n\n"
        )
        if "see_also" in entry and entry["see_also"]:
            message += f"🔗 *See Also:* {', '.join(entry['see_also'])}\n\n"
            
        message += (
            f"--- \n"
            f"💪 *Stress Test:* Can you use '{entry['word'].lower()}' in a sentence today?"
        )
        
        bot_username = context.bot.username
        keyboard = [[InlineKeyboardButton("🤖 View Bot", url=f"https://t.me/{bot_username}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        for chat_id in chat_ids:
            try:
                db.add_word_to_vocabulary(chat_id, entry['word'])
                await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', reply_markup=reply_markup)
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")

async def send_golden_list(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    recent, unlearned = db.get_golden_list(chat_id)
    if not recent and not unlearned:
        try:
            await context.bot.send_message(chat_id=chat_id, text="You haven't added any words to your vocabulary yet!")
        except Exception:
            pass
        return

    all_words = recent + unlearned
    seen = set()
    unique_words = []
    for w, learned in all_words:
        if w not in seen:
            seen.add(w)
            unique_words.append((w, learned))
            
    unique_words = unique_words[:100]

    keyboard = []
    for w, learned in unique_words:
        short_w = w[:50]
        text = f"✅ {w}" if learned else f"❌ {w}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"vocab_{short_w}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🏆 *Your Golden List*\n\n"
        "Review your vocabulary over the past 2 weeks and all unlearned words. "
        "Tap a word to toggle its status:\n\n"
        "(✅ = Learned, ❌ = Unlearned)"
    )
    
    try:
        await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_markup, parse_mode='Markdown')
    except Exception as e:
        print(f"Failed to send golden list to {chat_id}: {e}")

async def goldenlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    await send_golden_list(context, user_id)

async def send_all_golden_lists(context: ContextTypes.DEFAULT_TYPE):
    epoch = datetime.date(2026, 4, 8)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    if (today - epoch).days % 14 != 0:
        return

    users = db.get_all_users()
    for chat_id, _ in users:
        await send_golden_list(context, chat_id)

async def test_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_daily_words(context)
    await update.message.reply_text("Sent daily words to all users.")

import time as time_module

def main():
    db.init_db()
    
    if not TOKEN:
        print("Please set the TOKEN environment variable before running.")
        return
        
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Flask web server started in background.")

    retry_delay = 5
    while True:
        try:
            application = ApplicationBuilder().token(TOKEN).build()
            
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("level", level_command))
            application.add_handler(CommandHandler("test", test_send))
            application.add_handler(CommandHandler("goldenlist", goldenlist_command))
            application.add_handler(CallbackQueryHandler(button_callback))

            t = datetime.time(hour=6, minute=0, tzinfo=datetime.timezone.utc)
            application.job_queue.run_daily(send_daily_words, time=t)
            
            t_golden = datetime.time(hour=10, minute=0, tzinfo=datetime.timezone.utc)
            application.job_queue.run_daily(send_all_golden_lists, time=t_golden)
            
            print("Bot is starting. Press Ctrl+C to stop.")
            retry_delay = 5
            application.run_polling(drop_pending_updates=True)
        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Conflict:
            print("Conflict error: another instance is running. Waiting 60s for it to terminate...")
            time_module.sleep(60)
        except Exception as e:
            print(f"Bot crashed with error: {e}. Restarting in {retry_delay}s...")
            time_module.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)

if __name__ == '__main__':
    main()
