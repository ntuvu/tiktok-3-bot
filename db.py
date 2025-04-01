import asyncio
import os

from dotenv import load_dotenv
from postgrest import APIResponse
from supabase import create_client, Client

from fetch import fetch_tiktok_videos

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)


# get random video link
def get_video_link() -> str:
    response: APIResponse = supabase.rpc("get_video_link").execute()
    link: str = response.data
    return link


def get_user() -> list:
    response: APIResponse = supabase.rpc("get_user_not_fetch").execute()
    return response.data


def update_user_to_fetched(tiktok_user: str) -> None:
    users_dict: dict = {"tiktok_user": tiktok_user, "fetched": 1}

    response = (
        supabase.table("tiktok_user")
        .update(users_dict)
        .execute()
    )


async def insert_all_video() -> None:
    # users = get_user()
    users = ['zinzinnn2003']
    print(f'users: {users}')
    videos: list[tuple[str, str, str]] = []
    for user in users:
        fetched_videos = await fetch_tiktok_videos(user)
        if fetched_videos:  # Ensure fetched_videos is not None or empty
            videos += fetched_videos
            print(f"Fetched videos for user {user}: {fetched_videos}")

    if videos:  # Ensure videos list is not empty before inserting
        res_dict = [{"video_id": video_id, "link": play, "user": user} for video_id, play, user in videos]
        print('res_dict:', res_dict)

        response = (
            supabase.table("video")
            .insert(res_dict)
            .execute()
        )
        print(f"Inserted {len(videos)} videos:", response)

    for user in users:
        update_user_to_fetched(user)
        print(f"Updated user {user} to fetched status")


asyncio.run(insert_all_video())
