# TikTok Bot
A Python-based Telegram bot that enables users to download and process TikTok videos through a convenient chat interface.
## Project Overview
This project implements a Telegram bot that allows users to:
- Download TikTok videos
- Process video requests
- Store video metadata in a Supabase database
- Schedule periodic tasks for data processing

## Tech Stack
- **Python 3.x**: Core programming language
- **Aiogram 3.19.0**: Telegram Bot framework
- **Supabase 2.15.0**: Backend database service
- **Dotenv**: Environment variable management
- **Postgrest 1.0.1**: REST API for PostgreSQL database

## Project Structure
``` 
tiktok-3-bot/
├── app/
│   ├── __init__.py
│   ├── bot.py            # Bot implementation
│   ├── download_services.py # Video downloading functionality
│   ├── db_services.py    # Database interaction services
│   └── periodic_tasks.py # Scheduled tasks
├── bot.py               # Main bot entry point
├── db.py                # Database configuration
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies
└── .gitignore          # Git ignore file
```
## Installation
1. Clone the repository:
``` bash
git clone https://github.com/yourusername/tiktok-3-bot.git
cd tiktok-3-bot
```
1. Install dependencies:
``` bash
pip install -r requirements.txt
```
1. Create a `.env` file with the following variables:
``` 
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```
## Usage
1. Start the bot:
``` bash
python main.py
```
1. Interact with the bot on Telegram by sending TikTok video links.
2. The bot will respond with the downloaded video or appropriate error messages.

## Features
- **TikTok Video Download**: Extract and download videos from TikTok links
- **Database Integration**: Store video metadata and user information
- **Error Handling**: Robust error handling for invalid links and failed downloads
- **Periodic Tasks**: Scheduled tasks for maintenance and data processing
