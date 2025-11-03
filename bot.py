import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from textblob import TextBlob

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # set in Render environment
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "YourUsername")  # without @
OMDB_API_KEY = os.getenv("OMDB_API_KEY")  # get from https://www.omdbapi.com/apikey.aspx

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Send me a movie name and I’ll show poster, rating, and more!"
    )

async def movie_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    # Spell correction
    corrected = str(TextBlob(query).correct())
    if corrected.lower() != query.lower():
        await update.message.reply_text(f"🔍 Did you mean {corrected}?", parse_mode="Markdown")
        query = corrected

    # Fetch data from OMDb
    url = f"https://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        title = response.get("Title")
        year = response.get("Year")
        rating = response.get("imdbRating")
        poster = response.get("Poster")

        text = f"🎬 {title} ({year})\n⭐ IMDb: {rating}"
        keyboard = [
            [InlineKeyboardButton(f"📩 Contact @{OWNER_USERNAME}", url=f"https://t.me/{OWNER_USERNAME}?text={title}%20movie%20request")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_photo(photo=poster, caption=text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Movie not found. Try another name!")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, movie_info))

    print("🤖 Bot started...")
    app.run_polling()

if _name_ == "_main_":
    main()
