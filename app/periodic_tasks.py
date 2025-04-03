# app/periodic_tasks.py
import asyncio
import logging
import os

from aiogram import Bot
from dotenv import load_dotenv
from app.db_services import get_list_chat_id

load_dotenv()

CHAT_ID: str = os.getenv('CHAT_ID', '')
WEEKLY_INTERVAL: int = 7 * 24 * 60 * 60  # One week in seconds


async def start_hello_task(bot: Bot):
    list_chat_id = await get_list_chat_id()
    chat_ids = [item["chat_id"] for item in list_chat_id]
    print(chat_ids)
    while True:
        try:
            # for chat_id in chat_ids:
            #     if chat_id:
            #         await bot.send_message(chat_id.strip(), "Hello mấy cưng chụy comback đây")
            await bot.send_message(CHAT_ID, "Hello mấy cưng chụy comback đây")
        except Exception as e:
            logging.error(f"Error sending periodic message: {e}")
        await asyncio.sleep(WEEKLY_INTERVAL)
