import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

# Получение токена из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

# === ИСТОЧНИКИ МЕМОВ ===

def get_meme_api():
    r = requests.get("https://meme-api.com/gimme")
    data = r.json()
    return {"url": data["url"], "title": data["title"]}

def get_imgflip():
    r = requests.get("https://api.imgflip.com/get_memes")
    meme = random.choice(r.json()["data"]["memes"])
    return {"url": meme["url"], "title": meme["name"]}

def get_memegen():
    return {"url": "https://api.memegen.link/images/buzz/memes/memes_everywhere.png", "title": "Memes Everywhere"}

def get_apimeme():
    return {"url": "http://apimeme.com/meme?meme=Condescending-Wonka&top=Top+Text&bottom=Bottom+Text", "title": "Condescending Wonka"}

def get_supermeme():
    return {"url": "https://supermeme.ai/sample-meme.jpg", "title": "AI Generated Meme"}


MEME_SOURCES = [get_meme_api, get_imgflip, get_memegen, get_apimeme, get_supermeme]

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Ещё мем", callback_data="more_meme")]
    ])

# === ЛОГИКА ОТПРАВКИ МЕМОВ ===

async def send_meme(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    meme_func = random.choice(MEME_SOURCES)
    try:
        meme = meme_func()
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_photo(
                photo=meme["url"], caption=meme["title"], reply_markup=get_keyboard()
            )
        else:
            await update_or_query.message.edit_media(
                media=InputMediaPhoto(media=meme["url"], caption=meme["title"]),
                reply_markup=get_keyboard()
            )
    except Exception as e:
        print("Ошибка:", e)
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text("Не удалось получить мем 😢")
        else:
            await update_or_query.message.edit_message_text("Ошибка. Попробуй позже 🙁")

async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_meme(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "more_meme":
        await send_meme(query, context)

# === ЗАПУСК БОТА ===

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("meme", meme_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling(drop_pending_updates=True)

