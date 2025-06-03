import os
import random
import requests
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, Application
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# === Проверка URL ===
def is_url_image(url):
    try:
        r = requests.head(url, timeout=5)
        content_type = r.headers.get("Content-Type", "")
        return content_type.startswith("image/")
    except:
        return False

# === Источники, которые точно работают ===

def get_meme_api():
    r = requests.get("https://meme-api.com/gimme")
    data = r.json()
    return {"url": data["url"], "title": data["title"]}

def get_fixed_static_ru():
    images = [
        "https://memes.znanio.ru/wp-content/uploads/2023/07/mem-1.jpg",
        "https://memes.znanio.ru/wp-content/uploads/2023/07/mem-2.jpg",
        "https://memes.znanio.ru/wp-content/uploads/2023/07/mem-3.jpg"
    ]
    url = random.choice(images)
    return {"url": url, "title": "Znanio мем"}

def get_dino_mem():
    dino_urls = [
        "https://i.pinimg.com/originals/79/b6/8e/79b68ef94dd659d4070d0e88ef179baa.jpg",
        "https://i.pinimg.com/originals/4c/ae/e3/4caee3b3b40b27855c989bb56bd64fa8.jpg",
        "https://i.pinimg.com/originals/c2/8a/c4/c28ac46a7bce768e63c3c25187935452.jpg"
    ]
    return {"url": random.choice(dino_urls), "title": "Динозавр-мем 🦖"}

MEME_SOURCES = [get_meme_api, get_fixed_static_ru, get_dino_mem]

# === Кнопки ===
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Ещё мем", callback_data="more_meme")]
    ])

# === Отправка мема ===
async def send_meme(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    for _ in range(5):  # Попытки до 5 раз
        meme = random.choice(MEME_SOURCES)()
        if is_url_image(meme["url"]):
            try:
                if isinstance(update_or_query, Update):
                    await update_or_query.message.reply_photo(
                        photo=meme["url"], caption=meme["title"], reply_markup=get_keyboard()
                    )
                else:
                    await update_or_query.edit_message_media(
                        media=InputMediaPhoto(media=meme["url"], caption=meme["title"]),
                        reply_markup=get_keyboard()
                    )
                return
            except Exception as e:
                print("Ошибка при отправке мема:", e)
    # Если ни один не сработал
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text("Не удалось получить мем 😿")
    else:
        await update_or_query.edit_message_caption(caption="Не удалось загрузить мем 😿")

# === Команды ===
async def meme_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_meme(update, context)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_meme(update.callback_query, context)

# === Удаление webhook при старте ===
async def delete_webhook_on_startup(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook очищен")

# === Инициализация ===
app = ApplicationBuilder().token(TOKEN).post_init(delete_webhook_on_startup).build()
app.add_handler(CommandHandler("meme", meme_command))
app.add_handler(CallbackQueryHandler(button_callback))
app.run_polling(
    allowed_updates=Update.ALL_TYPES,
    drop_pending_updates=True
)


