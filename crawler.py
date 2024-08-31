import asyncio
import httpx
import os
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO


MAX_CONCURRENT_DOWNLOADS = 3


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
}


async def process_multi_chapter(url, start_chap, end_chap, path):
    os.makedirs(path, exist_ok=True)
    async with httpx.AsyncClient(http2=True, headers=headers) as client:
        tasks = []
        semaphore = asyncio.Semaphore(
            MAX_CONCURRENT_DOWNLOADS
        )  # Limit concurrent tasks
        for i in range(start_chap, end_chap + 1):
            tasks.append(process_single_chapter(client, url, i, path, semaphore))

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(e)


async def process_single_chapter(client, url, chapter, path, semaphore):
    async with semaphore:
        html_content = await get_html_content(client, url, chapter)
        img_host_url = find_chapter_img_host_url(html_content)
        num_imgs = find_chapter_num_imgs(html_content)
        base_url = (
            f'https://{img_host_url}/{"/".join([part for part in url.split("/")[-2:]])}'
        )

        ################################ Save to images #################################
        # chapter_path = f"{path}chapter_{i:04d}"
        # os.makedirs(chapter_path, exist_ok=True)
        # tasks = []
        # for i in range(1, num_imgs + 1):
        #     img_name = f"{chapter:04d}-{i:03d}.png"
        #     img_url = f"{base_url}/{img_name}"
        #     tasks.append(
        #         download_and_save_image(client, img_url, f"{chapter_path}/{img_name}")
        #     )

        # await asyncio.gather(*tasks)

        ################################# Save to pdfs #################################
        images = [None] * num_imgs  # List to hold image bytes

        # Fetch all images concurrently
        tasks = []
        for i in range(1, num_imgs + 1):
            img_name = f"{chapter:04d}-{i:03d}.png"
            img_url = f"{base_url}/{img_name}"
            tasks.append(fetch_image(client, img_url, i - 1, images))

        await asyncio.gather(*tasks)

        # Save all images in the list directly to a PDF
        chapter_path = f"{path}chapter_{chapter:04d}.pdf"
        images[0].save(
            chapter_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:],
        )
        images.clear()


async def fetch_image(client, img_url, index, images):
    img_data = await process_single_page(client, img_url)
    image = Image.open(BytesIO(img_data)).convert("RGB")  # Convert image to RGB
    images[index] = image  # Place image in the correct position


async def download_and_save_image(client, url, path):
    try:
        print(url)
        img_data = await process_single_page(client, url)
        with open(path, "wb") as file:
            file.write(img_data)
    except Exception as e:
        print(e)


async def process_single_page(client, url):
    print("Processing", url)
    response = await client.get(url)
    if response.status_code == 200:
        return response.content
    raise Exception(f"Couldn't find {url}")


async def get_html_content(client, url, chapter):
    name = url.split("/")[-1]
    html_link = f"https://manga4life.com/read-online/{name}-chapter-{chapter}.html"
    response = await client.get(html_link)
    soup = BeautifulSoup(response.text, "html.parser")
    if "404" in soup.title.text:
        raise Exception(f"Couldn't find {html_link}")
    return soup


def find_chapter_img_host_url(html_content):
    """Find the hosting url where the images of chapter is in by html"""
    scripts = html_content.find_all("script")
    for script in scripts:
        if script.string:
            script_content = script.string.strip()
            match = re.search(r'vm\.CurPathName\s*=\s*"([^"]+)"', script_content)
            if match:
                return match.group(1)


def find_chapter_num_imgs(html_content):
    """Find the number of images of the chapter by html"""
    scripts = html_content.find_all("script")
    for script in scripts:
        if script.string:
            script_content = script.string.strip()
            match = re.search(
                r'vm\.CurChapter\s*=\s*\{.*?"Page":"(\d+)"', script_content
            )
            if match:
                return int(match.group(1))


# # To run the async functions
# asyncio.run(
#     process_multi_chapter("https://manga4life.com/manga/Vagabond", 1, 10, "Vagabond/")
# )
