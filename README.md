# 🎬 Movie Info Telegram Bot

A Telegram bot that:
- Shows movie posters, ratings (IMDb)
- Corrects spelling
- Has contact button to message the owner

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get OMDb API key: https://www.omdbapi.com/apikey.aspx
3. Set these Render Environment Variables:
   - BOT_TOKEN = your bot token
   - OMDB_API_KEY = your OMDb key
   - OWNER_USERNAME = your Telegram username (without @)
4. Deploy on Render with:
   - Build command: pip install -r requirements.txt
   - Start command: python bot.py
