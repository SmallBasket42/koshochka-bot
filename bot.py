import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# Мем-источники (простые картинки)
def get_meme_api():
    r = requests.get("https://meme-api.com/gimme")
    data = r.json()
    return {"url": data["url"], "title": data["title"]}

def get_nekobot():
    r = requests.get("https://nekobot.xyz/api/image?type=meme")
    return {"url": r.json()["message"], "title": "НекоБот мем"}

def get_static_ru():
    return {"url": "https://memes.znanio.ru/wp-content/uploads/2023/07/mem-1.jpg", "title": "Znanio мем"}

def get_picsum():
    return {"url": "https://picsum.photos/400", "title": "Случайное изображение"}

MEME_SOURCES = [get_meme_api, get_nekobot, get_static_ru, get_picsum]

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Ещё мем", callback_data="more_meme")]
    ])

async def send_meme(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    meme = random.choice(MEME_SOURCES)()
    if not meme["url"].endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")) and "picsum.photos" not in meme["url"]:
        raise ValueError("Unsupported image format")

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_photo(
            photo=meme["url"], caption=meme["title"], reply_markup=get_keyboard()
        )
    else:
        await update_or_query.edit_message_media(
            media=InputMediaPhoto(media=meme["url"], caption=meme["title"]),
            reply_markup=get_keyboard()
        )

async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_meme(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_meme(update.callback_query, context)

# Удаляем все старые Webhook/Polling подключения
async def reset_webhook(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

app = ApplicationBuilder().token(TOKEN).post_init(reset_webhook).build()
app.add_handler(CommandHandler("meme", meme_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling(
    allowed_updates=Update.ALL_TYPES,
    drop_pending_updates=True
)
