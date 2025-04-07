# app/bot.py
import asyncio
import io
import os

from aiogram import Bot, Dispatcher
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

from app.db_services import get_random_video, delete_video, inactive_video, get_list_chat_id
from app.decoration import auth_check, roles_check
from app.download_services import get_video_async

load_dotenv()

# Environmental variables
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHAT_ID: str = os.getenv("CHAT_ID", "")

user_router = Router()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Command handlers
@dp.message(Command("hello"))
@auth_check
async def handle_hello(message: Message) -> None:
    """Send a greeting."""
    await message.reply("Hello there! 👋")


@dp.message(Command("start"))
@auth_check
async def handle_start(message: Message) -> None:
    """Send a welcome message."""
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("chatid"))
@auth_check
async def handle_chat_id(message: Message) -> None:
    """Send the current chat ID."""
    await message.reply(f"Your chat ID is: {message.chat.id}")


@dp.message(Command("download"))
@auth_check
async def handle_download(message: Message) -> None:
    """Download a video from a TikTok URL provided in the message."""
    video_url = message.text.split(" ", 1)[-1]  # Get the TikTok URL from the message

    if not video_url.startswith("http"):
        await message.reply("Please provide a valid TikTok URL.")
        return

    video_path = await get_video_async(video_url)
    try:
        await message.reply("Downloading your TikTok video... 📥")

        # Load video into memory with BytesIO
        with open(video_path, "rb") as video_file:
            video_data = io.BytesIO(video_file.read())
            video_data.seek(0)  # Reset buffer pointer to start of the file

        # Send the video using InputFile
        video_to_send = FSInputFile(video_path, filename="video.mp4")
        await bot.send_video(chat_id=message.chat.id, video=video_to_send)

    except Exception as e:
        await message.reply(f"An error occurred: {e}")

    finally:
        # Clean up: Close buffer and delete the local file
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("random"))
@auth_check
async def get_random_video_command(message: Message) -> None:
    # Start by notifying the user immediately
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

    # Get random video URL
    video_url = await get_random_video()
    if not video_url:
        await message.reply("No video found.")
        return

    video_path = None  # Define video_path outside the try block

    try:
        # Start the download process
        download_task = asyncio.create_task(get_video_async(video_url))

        # While video is downloading, we can update the user
        send_action_task = asyncio.create_task(
            bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
        )

        # Wait for download to complete
        video_path = await download_task
        if not video_path:
            await message.reply("Sorry, couldn't download that video.")
            return

        # Wait for notification to complete if it hasn't already
        await send_action_task

        # Send the video directly from the file path without loading it into memory
        video_to_send = FSInputFile(video_path, filename="video.mp4")
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_to_send,
            caption=f"{video_url}",
            width=320,
            height=180
        )

        # Clean up the downloaded file after successful sending
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        # Handle the error
        await message.reply(f"An error occurred: {e}")

        # Also clean up the file in case of error
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("delete"))
@auth_check
@roles_check
async def delete_video_command(message: Message) -> None:
    video_url = message.reply_to_message.caption
    if not video_url or not video_url.startswith("http"):
        await message.reply("Please provide a valid TikTok URL.")
        return

    try:
        asyncio.create_task(delete_video(video_url))
    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply(f"An error occurred: {e}")
    finally:
        print(f"Video {video_url} deleted.")
        await message.reply("Video deleted.")


@dp.message(Command("inactive"))
@auth_check
async def delete_video_command(message: Message) -> None:
    video_url = message.reply_to_message.caption
    if not video_url or not video_url.startswith("http"):
        await message.reply("Please provide a valid TikTok URL.")
        return

    try:
        asyncio.create_task(inactive_video(video_url))
    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply(f"An error occurred: {e}")
    finally:
        print(f"Video {video_url} inactive.")
        await message.reply("Video inactive.")


@dp.message(Command("test"))
async def test_reply(message: Message) -> None:
    if message.reply_to_message:  # Kiểm tra xem tin nhắn có phải là reply không
        replied_text = message.reply_to_message.caption  # Lấy nội dung tin nhắn gốc
        await message.answer(f"Bạn đã trả lời: {replied_text}")
    else:
        await message.answer("Hãy reply vào một tin nhắn nào đó.")


# send message to chat_id in db
@dp.message(Command("send"))
@roles_check
async def send_message_to_chat_id(message: Message) -> None:
    content = message.text.split(" ", 1)[-1]  # Extract the content after the command

    chat_ids = [item["chat_id"] for item in await get_list_chat_id()]
    print(f"list chat send video: {chat_ids}")

    if not content:
        await message.reply("Please provide a message to send.")
        return

    for chat_id in chat_ids:
        if chat_id:
            await bot.send_message(chat_id.strip(), content)
