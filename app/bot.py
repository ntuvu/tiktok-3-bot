# app/bot.py
import asyncio
import io
import os

from aiogram import Bot, Dispatcher
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

from app.db_services import get_random_video, delete_video, inactive_video, get_list_chat_id, get_random_user_video, add_tiktok_user
from app.decorator.authen import auth_check, roles_check
from app.decorator.rate_limiter import rate_limit
from app.download_services import get_video_async
from app.utils import extract_link_from_caption, extract_tiktok_username

load_dotenv()

# Environmental variables
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHAT_ID: str = os.getenv("CHAT_ID", "")

user_router = Router()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Command handlers
@dp.message(Command("hello"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def handle_hello(message: Message) -> None:
    """Send a greeting."""
    await message.reply("Hello there! 👋")


@dp.message(Command("start"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def handle_start(message: Message) -> None:
    """Send a welcome message."""
    await message.reply("Welcome! Send /hello to get a greeting.")


@dp.message(Command("chatid"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def handle_chat_id(message: Message) -> None:
    """Send the current chat ID."""
    await message.reply(f"Your chat ID is: {message.chat.id}")


@dp.message(Command("download"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
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


@dp.message(Command("r"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def get_random_video_command(message: Message) -> None:
    await send_random_video(message)


@dp.message(Command("ru"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def get_random_user_video_command(message: Message) -> None:
    url = message.text.split(" ", 1)[-1]
    await send_random_video(message, url)


@dp.message(Command("d"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
@roles_check
async def delete_video_command(message: Message) -> None:
    caption = message.reply_to_message.text
    if not caption:
        await message.reply("Please provide a valid TikTok URL.")
        return

    video_url = extract_link_from_caption(caption)
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


@dp.message(Command("i"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@auth_check
async def delete_video_command(message: Message) -> None:
    caption = message.reply_to_message.text
    if not caption:
        await message.reply("Please provide a valid TikTok URL.")
        return

    video_url = extract_link_from_caption(caption)
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


# add tiktok user
@dp.message(Command("add"))
@rate_limit(cooldown = 10, message="Đừng có spam.")
@roles_check
async def add_tiktok_user_command(message: Message) -> None:
    command_params = message.text.strip().split(" ", 1)[-1]
    tiktok_username = command_params

    if not tiktok_username:
        await message.reply("Please provide a tiktok user to send.")
        return

    response = await add_tiktok_user(tiktok_username)

    if response:
        await message.reply(response)
    else:
        await message.reply(f"Failed to add tiktok user {tiktok_username}.")


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


async def send_random_video(message: Message, user=None) -> None:
    # Start by notifying the user immediately
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

    # Get random video URL
    print(f"user: {user}")
    video_url = await get_random_user_video(user) if user else await get_random_video()
    print(f"video_url: {video_url}")
    if not video_url:
        await message.reply("No video found.")
        return

    video_path = None
    try:
        # Start the download process and notification
        download_task = asyncio.create_task(get_video_async(video_url))
        action_task = asyncio.create_task(
            bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
        )

        # Wait for download to complete
        video_path = await download_task
        if not video_path:
            await message.reply("Sorry, couldn't download that video.")
            return

        # Wait for notification to complete if it hasn't already
        await action_task

        # Send the video directly from the file path
        video_to_send = FSInputFile(video_path, filename="video.mp4")
        # get username in video_url
        username = extract_tiktok_username(video_url)

        # change send video logic to make video sent smaller
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_to_send,
        )
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"link: {video_url}, username: {username}",
            disable_notification=True,
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.reply(f"An error occurred: {e}")
    finally:
        # Clean up the downloaded file regardless of outcome
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
