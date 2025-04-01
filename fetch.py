import asyncio

import aiohttp


async def fetch_tiktok_videos(user: str) -> list[tuple[str, str, str]]:
    url: str = "https://tiktok-video-no-watermark2.p.rapidapi.com/user/posts"

    querystring: dict[str, str] = {"unique_id": f"@{user}", "count": "35", "cursor": "0"}

    headers: dict[str, str] = {
        "x-rapidapi-key": "ab98b7b7f9mshf66db49ca656311p19f1f5jsn66e8eba7d3f3",
        "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }

    videos = []
    cursor = "0"

    async with aiohttp.ClientSession() as session:
        while True:
            querystring["cursor"] = cursor
            async with session.get(url, headers=headers, params=querystring) as response:
                data = await response.json()
                data = data['data']
                videos.extend(data['videos'])
                if not data['hasMore']:
                    break
                cursor = data['cursor']

    res: list[tuple[str, str, str]] = [
        (video['video_id'], video['play'], user) for video in videos
    ]
    print(res)
    return res


asyncio.run(fetch_tiktok_videos("zinzinnn2003"))
