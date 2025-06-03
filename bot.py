import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Источник 1: meme-api.com
def get_meme_api():
    r = requests.get("https://meme-api.com/gimme")
    data = r.json()
    return {"url": data["url"], "title": data["title"]}

# Источник 2: imgflip (без токена)
def get_imgflip():
    r = requests.get("https://api.imgflip.com/get_memes")
    data = r.json()
    meme = random.choice(data["data"]["memes"])
    return {"url": meme["url"], "title": meme["name"]}

# Источник 3: memezz.com
def get_memezz():
    r = requests.get("https://memezz.com/api/v1/meme/random")
    data = r.json()
    return {"url": data["meme"]["url"], "title": data["meme"]["title"]}

# Список всех источников
MEME_SOURCES = [get_meme_api, get_imgflip, get_memezz]

# Кнопка
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Ещё мем", callback_data="more_meme")]
    ])

# Отправка мема
async def send_meme(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    meme_func = random.choice(MEME_SOURCES)
    try:
        meme = meme_func()
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_photo(
                photo=meme["url"],
                caption=meme["title"],
                reply_markup=get_keyboard()
            )
        else:
            await update_or_query.message.edit_media(
                media=InputMediaPhoto(media=meme["url"], caption=meme["title"]),
                reply_markup=get_keyboard()
            )
    except Exception as e:
        print("Ошибка при получении мема:", e)
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text("Не удалось получить мем 😢")
        else:
            await update_or_query.message.edit_message_text("Мем не найден. Попробуй позже 🙁")

# Команда /meme
async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_meme(update, context)

# Кнопка "ещё мем"
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "more_meme":
        await send_meme(query, context)

# === Запуск ===
TOKEN = "8135269098:AAEiL99eCR9bo9K3sqqeQea2pgcFeSAuEjI"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("meme", meme_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling()
