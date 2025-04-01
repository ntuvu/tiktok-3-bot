# app/periodic_tasks.py
import asyncio
import logging
import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

CHAT_ID: str = os.getenv('CHAT_ID', '')
WEEKLY_INTERVAL: int = 7 * 24 * 60 * 60  # One week in seconds


async def start_hello_task(bot: Bot):
    """Send periodic hello messages."""
    while True:
        try:
            await bot.send_message(CHAT_ID, "Hello!")
        except Exception as e:
            logging.error(f"Error sending periodic message: {e}")
        await asyncio.sleep(WEEKLY_INTERVAL)
