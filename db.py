import os

from dotenv import load_dotenv
from postgrest import APIResponse
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)


# get random video link
def get_video_link() -> str:
    response: APIResponse = supabase.rpc("get_video_link").execute()
    link: str = response.data
    return link
