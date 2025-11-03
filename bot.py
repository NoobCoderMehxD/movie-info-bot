import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from textblob import TextBlob

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # from Render environment
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "YourUsername")  # without @
OMDB_API_KEY = os.getenv("OMDB_API_KEY")  # from https://www.omdbapi.com/apikey.aspx


# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start message"""
    msg = (
        "👋 *Welcome to Movie Info Bot!*\n\n"
        "🎬 Just send me any movie name and I’ll show:\n"
        "• Poster\n"
        "• IMDb rating\n"
        "• Release year\n\n"
        "📩 Use /help to learn more commands."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    msg = (
        "🆘 *Help Menu*\n\n"
        "Here’s how to use this bot:\n"
        "1️⃣ Type any movie name (e.g., Inception)\n"
        "2️⃣ Get poster, IMDb rating, and release year\n"
        "3️⃣ Tap the contact button to message the owner\n\n"
        "💡 Example:\n"
        "Avngers → the bot will auto-correct it to Avengers.\n\n"
        "📩 Contact: [@{username}](https://t.me/{username})"
    ).format(username=OWNER_USERNAME)
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)


# === MOVIE INFO HANDLER ===
async def movie_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user movie queries"""
    query = update.message.text.strip()
    print(f"🎬 Searching for movie: {query}")  # Debug log

    # === Try original query first ===
    url = f"https://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    response = requests.get(url).json()
    print("🔎 OMDb Response:", response)  # Debug log

    # === If not found, try corrected spelling ===
    if response.get("Response") != "True":
        corrected = str(TextBlob(query).correct())
        if corrected.lower() != query.lower():
            print(f"🪄 Trying corrected spelling: {corrected}")
            url = f"https://www.omdbapi.com/?t={corrected}&apikey={OMDB_API_KEY}"
            response = requests.get(url).json()
            print("🔎 Corrected Response:", response)
            if response.get("Response") == "True":
                await update.message.reply_text(
                    f"🔍 Did you mean *{corrected}*?", parse_mode="Markdown"
                )

    # === Process OMDb response ===
    if response.get("Response") == "True":
        title = response.get("Title", "Unknown")
        year = response.get("Year", "N/A")
        rating = response.get("imdbRating", "N/A")
        poster = response.get("Poster", None)

        # Handle missing posters
        if not poster or poster == "N/A":
            poster = None

        text = f"🎬 *{title}* ({year})\n⭐ IMDb: {rating}"

        # Inline button
        keyboard = [
            [
                InlineKeyboardButton(
                    f"📩 Contact @{OWNER_USERNAME}",
                    url=f"https://t.me/{OWNER_USERNAME}?text={title}%20movie%20request",
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send poster or fallback to text
        if poster:
            await update.message.reply_photo(
                photo=poster,
                caption=text,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

    else:
        await update.message.reply_text("❌ Movie not found. Try another name!")


# === MAIN ===
def main():
    if not BOT_TOKEN or not OMDB_API_KEY:
        print("⚠️ Missing environment variables! Please set BOT_TOKEN and OMDB_API_KEY.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, movie_info))

    print("🤖 Bot started and polling for updates...")
    app.run_polling()


if __name__ == "__main__":
    main()
