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
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables!")

# === ИСТОЧНИКИ МЕМОВ ===

def get_meme_api():
    r = requests.get("https://meme-api.com/gimme")
    data = r.json()
    return {"url": data["url"], "title": data["title"]}

def get_imgflip():
    r = requests.get("https://api.imgflip.com/get_memes")
    memes = r.json()["data"]["memes"]
    meme = random.choice(memes)
    return {"url": meme["url"], "title": meme["name"]}

def get_memegen():
    return {"url": "https://api.memegen.link/images/buzz/top/bottom.png", "title": "Memegen Buzz"}

def get_nekobot():
    r = requests.get("https://nekobot.xyz/api/image?type=meme")
    data = r.json()
    return {"url": data["message"], "title": "НекоБот мем"}

def get_znanija_meme():
    return {"url": "https://memes.znanio.ru/wp-content/uploads/2023/07/mem-1.jpg", "title": "Znanio мем"}

def get_randompic_meme():
    r = requests.get("https://randstuff.ru/picture/")
    return {"url": "https://randstuff.ru/picture/i/", "title": "Случайная картинка"}

def get_picsum_meme():
    return {"url": "https://picsum.photos/400", "title": "Случайная картинка"}

MEME_SOURCES = [
    get_meme_api,
    get_imgflip,
    get_memegen,
    get_nekobot,
    get_znanija_meme,
    get_randompic_meme,
    get_picsum_meme
]

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Ещё мем", callback_data="more_meme")]
    ])

async def send_meme(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    meme_func = random.choice(MEME_SOURCES)
    try:
        meme = meme_func()
        if not any(meme["url"].endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]) and "picsum.photos" not in meme["url"]:
            raise ValueError("Неподдерживаемый формат мема")

        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_photo(
                photo=meme["url"], caption=meme["title"], reply_markup=get_keyboard()
            )
        else:
            await update_or_query.edit_message_media(
                media=InputMediaPhoto(media=meme["url"], caption=meme["title"]),
                reply_markup=get_keyboard()
            )

    except Exception as e:
        print("Ошибка:", e)
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text("Ошибка. Попробуй позже 🙁")
        else:
            try:
                await update_or_query.edit_message_caption(caption="Ошибка. Попробуй позже 🙁")
            except:
                pass

async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_meme(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_meme(query, context)

# === ЗАПУСК БОТА ===

async def reset_webhook(app):
    await app.bot.delete_webhook(drop_pending_updates=True)

app = ApplicationBuilder().token(TOKEN).post_init(reset_webhook).build()
app.add_handler(CommandHandler("meme", meme_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling(allowed_updates=Update.ALL_TYPES)


