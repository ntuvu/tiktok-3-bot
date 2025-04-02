# app/db_services.py
import os

from dotenv import load_dotenv
from postgrest import APIResponse
from supabase import create_client, Client

load_dotenv()

# Supabase client
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_random_video_link() -> str:
    try:
        response: APIResponse = supabase.rpc("get_video_link").execute()
        return response.data
    except Exception as e:
        print(f"Failed to get video link: {e}")
        return ""


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


def get_random_video():
    try:
        response: APIResponse = supabase.rpc("get_random_video").execute()
        return response.data
    except Exception as e:
        print(f"Failed to get random video: {e}")
        return ""


def delete_video(link: str):
    try:
        response: APIResponse = supabase.rpc("delete_video", {"p_link": link}).execute()
    except Exception as e:
        print(f"Failed to delete video: {e}")
        return False


def inactive_video(link: str):
    try:
        response: APIResponse = supabase.rpc("inactive_video", {"p_link": link}).execute()
    except Exception as e:
        print(f"Failed to inactive video: {e}")
        return False
