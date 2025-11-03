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
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "YourUsername")  # without @
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # get from https://www.themoviedb.org/settings/api


# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Welcome to Movie Info Bot!*\n\n"
        "🎬 Send any movie name (Telugu / Hindi / English) — I’ll show:\n"
        "• Poster\n"
        "• IMDb rating\n"
        "• Release year\n\n"
        "📩 Use /help for more."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🆘 *Help*\n\n"
        "Type any movie name (e.g., Pushpa, Inception, RRR)\n"
        "and I’ll show its details.\n\n"
        "📩 Contact: [@{username}](https://t.me/{username})"
    ).format(username=OWNER_USERNAME)
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True)


# === MOVIE INFO HANDLER ===
async def movie_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    print(f"🎬 Searching for: {query}")

    # Spell correction (optional)
    corrected = str(TextBlob(query).correct())
    if corrected.lower() != query.lower():
        await update.message.reply_text(f"🔍 Did you mean *{corrected}*?", parse_mode="Markdown")
        query = corrected

    # === TMDb search ===
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=en-IN"
    response = requests.get(search_url).json()
    print("🔎 TMDb Response:", response)

    if response.get("results"):
        movie = response["results"][0]  # Get top match
        title = movie.get("title")
        year = movie.get("release_date", "N/A")[:4]
        rating = movie.get("vote_average", "N/A")
        poster_path = movie.get("poster_path")

        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        text = f"🎬 *{title}* ({year})\n⭐ Rating: {rating}/10"

        keyboard = [[
            InlineKeyboardButton(
                f"📩 Contact @{OWNER_USERNAME}",
                url=f"https://t.me/{OWNER_USERNAME}?text={title}%20movie%20info"
            )
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if poster_url:
            await update.message.reply_photo(
                photo=poster_url,
                caption=text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

    else:
        await update.message.reply_text("❌ Movie not found. Try another name or correct spelling!")


# === MAIN ===
def main():
    if not BOT_TOKEN or not TMDB_API_KEY:
        print("⚠️ Missing environment variables! Set BOT_TOKEN and TMDB_API_KEY.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, movie_info))

    print("🤖 Bot started and polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
