# app/db_services.py
import asyncio
import os

from dotenv import load_dotenv
from postgrest import APIResponse
from supabase import create_client, Client

load_dotenv()

# Supabase client
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user_not_fetch():
    try:
        response: APIResponse = supabase.rpc("get_user_not_fetch").execute()
        return response.data
    except Exception as e:
        print(f"Failed to get user not fetch: {e}")
        return ""


def get_user_fetched():
    try:
        response: APIResponse = supabase.rpc("get_user_fetched").execute()
        return response.data
    except Exception as e:
        print(f"Failed to get user not fetch: {e}")
        return ""


# get random link video
async def get_random_video():
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("get_random_video").execute()
        )
        return response.data
    except Exception as e:
        print(f"Failed to get random video: {e}")
        return ""


# delete record by tiktok_link in video table
async def delete_video(link: str):
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("delete_video", {"p_link": link}).execute()
        )
        return response
    except Exception as e:
        print(f"Failed to delete video: {e}")
        return False


# set active = 0 in video table
async def inactive_video(link: str):
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("inactive_video", {"p_link": link}).execute()
        )
        return response

    except Exception as e:
        print(f"Failed to inactive video: {e}")
        return False


# insert to chat and tele_user table
async def add_chat_id_and_user_id(chat_id: str, user_id: str):
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("add_chat_id_and_user_id", {"p_chat_id": chat_id, "p_user_id": user_id}).execute()
        )
        return response
    except Exception as e:
        print(f"Failed to add chat id and user id: {e}")
        return False


# get current user info
async def get_current_tele_user_info(user_id: str):
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("get_current_tele_user_info", {"p_user_id": user_id}).execute()
        )
        return response.data
    except Exception as e:
        print(f"Failed to get current tele user info: {e}")
        return False


# get list chat_id
async def get_list_chat_id():
    try:
        response = await asyncio.to_thread(
            lambda: supabase.rpc("get_list_chat_id").execute()
        )
        return response.data
    except Exception as e:
        print(f"Failed to get list chat id: {e}")
        return False
