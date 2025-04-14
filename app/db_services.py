# app/db_services.py
import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Supabase client
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

# Connection pool
_supabase_client = None


def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


@asynccontextmanager
async def supabase_connection():
    client = get_supabase_client()
    try:
        yield client
    finally:
        # No explicit cleanup needed for supabase client
        pass


# Refactor functions to use the connection pool
async def get_random_video():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_random_video").execute()
            )
            # Return only needed data, not the entire response
            return response.data
    except Exception as e:
        print(f"Failed to get random video: {e}")
        return None


async def get_user_not_fetch():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_user_not_fetch").execute()
            )

            return response.data
    except Exception as e:
        print(f"Failed to get user not fetch: {e}")
        return ""


async def get_user_fetched():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_user_not_fetch").execute()
            )

            return response.data
    except Exception as e:
        print(f"Failed to get user not fetch: {e}")
        return ""


# delete record by tiktok_link in video table
async def delete_video(link: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("delete_video", {"p_link": link}).execute()
            )

            return response
    except Exception as e:
        print(f"Failed to delete video: {e}")
        return False


# set active = 0 in video table
async def inactive_video(link: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("inactive_video", {"p_link": link}).execute()
            )

            return response
    except Exception as e:
        print(f"Failed to inactive video: {e}")
        return False


# insert to chat and tele_user table
async def add_chat_id_and_user_id(chat_id: str, user_id: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("add_chat_id_and_user_id", {"p_chat_id": chat_id, "p_user_id": user_id}).execute()
            )

        return response
    except Exception as e:
        print(f"Failed to add chat id and user id: {e}")
        return False


# get current user info
async def get_current_tele_user_info(user_id: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_current_tele_user_info", {"p_user_id": user_id}).execute()
            )

        return response.data
    except Exception as e:
        print(f"Failed to get current tele user info: {e}")
        return False


# get list chat_id
async def get_list_chat_id():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_list_chat_id").execute()
            )

        return response.data
    except Exception as e:
        print(f"Failed to get list chat id: {e}")
        return False


async def get_random_user_video(tiktok_user: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_random_user_video", {"p_tiktok_user": tiktok_user}).execute()
            )
            return response.data
    except Exception as e:
        print(f"Failed to get random video: {e}")
        return None


async def add_tiktok_user(tiktok_user: str):
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("add_tiktok_user", {"p_tiktok_user": tiktok_user}).execute()
            )
            return response.data
    except Exception as e:
        print(f"Failed to get random video: {e}")
        return None


async def get_tiktok_user_video_counts():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_tiktok_user_video_counts").execute()
            )
            return response.data
    except Exception as e:
        print(f"Failed to get: {e}")
        return None


async def get_tiktok_user_frequency_summary():
    try:
        async with supabase_connection() as client:
            response = await asyncio.to_thread(
                lambda: client.rpc("get_tiktok_user_frequency_summary").execute()
            )
            return response.data
    except Exception as e:
        print(f"Failed to get: {e}")
        return None
