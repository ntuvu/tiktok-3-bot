# bot.py
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
CHAT_ID: str = os.getenv('CHAT_ID', '')

ONE_WEEK = 7 * 24 * 60 * 60  # 604800 seconds

bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()


@dp.message(Command("hello"))
async def send_hello(message: Message) -> None:
    await message.reply("Hello there! 👋")


@dp.message(Command("start"))
async def send_welcome(message: Message) -> None:
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("chatid"))
async def send_chat_id(message: Message) -> None:
    chat_id = message.chat.id
    await message.reply(f"Your chat ID is: {chat_id}")


async def send_hello_message():
    """Send a hello message every 10 seconds"""
    while True:
        try:
            await bot.send_message(CHAT_ID, "Hello!")
        except Exception as e:
            await bot.send_message(CHAT_ID, f'Error: {str(e)}')

        # Wait for 10 seconds before sending the next message
        await asyncio.sleep(ONE_WEEK)


async def on_startup() -> None:
    """Start the periodic message sender when the bot starts"""
    asyncio.create_task(send_hello_message())
