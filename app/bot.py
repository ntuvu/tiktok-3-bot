# app/bot.py
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Environmental variables
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHAT_ID: str = os.getenv("CHAT_ID", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Command handlers
@dp.message(Command("hello"))
async def handle_hello(message: Message) -> None:
    """Send a greeting."""
    await message.reply("Hello there! 👋")


@dp.message(Command("start"))
async def handle_start(message: Message) -> None:
    """Send a welcome message."""
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("chatid"))
async def handle_chat_id(message: Message) -> None:
    """Send the current chat ID."""
    await message.reply(f"Your chat ID is: {message.chat.id}")
