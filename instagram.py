from fastapi import FastAPI, HTTPException
from yarl import URL
import aiohttp
from bs4 import BeautifulSoup


app = FastAPI()


class Instagram:
    @staticmethod
    async def _fetch(session, url):
        async with session.get(url) as response:
            return await response.read()

    @staticmethod
    async def get_info(url: str):
        main_url = URL("https://ddinstagram.com")

        async with aiohttp.ClientSession() as session:
            async with session.get(url.replace("www.", "dd")) as response:
                resp = await response.read()

            soup = BeautifulSoup(resp.decode("utf-8"), "html.parser")

            download_urls = []

            video_path = soup.find("meta", property="og:video")
            image_path = soup.find("meta", property="og:image")

            if video_path:

                get_url = main_url.with_path(video_path["content"])

                async with session.get(get_url) as response_:
                    resp = response_.url

                    if not resp == get_url:
                        download_urls.append(str(resp))

            else:
                path_ = image_path["content"]
                post_id = path_.split("/")[2]

                if "grid" in path_:

                    paths = (f"/images/{post_id}/{i}" for i in range(1, 11))

                    for path_ in paths:
                        get_url = main_url.with_path(path_)
                        async with session.get(get_url) as response_:
                            resp = response_.url

                            if resp == get_url:
                                break
                            download_urls.append(str(resp))

                else:


                    get_url = main_url.with_path(path_)
                    async with session.get(get_url) as response_:
                        resp = response_.url
                        if not get_url == resp:
                            download_urls.append(str(resp))

            response = {
                "url": download_urls if len(download_urls) > 1 else download_urls[0],
            }
            return response
@app.get("/")
async def root():
    return {"message": "API is working!"}

@app.get("/api/v2/download", tags=['Version 2'])
async def get_instagram_media(url: str):
    try:
        info = await Instagram.get_info(url)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
