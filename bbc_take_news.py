import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup

async def fetch_content(session, url):
    async with session.get(url) as response:
        return await response.text()

async def process_link(session, link, news_file, link_file, processed_file):
    try:
        content = await fetch_content(session, link)
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('h1')
        if title:
            await news_file.write(title.text + '\n\n')
            title_text = title.text  
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            await news_file.write(paragraph.text + '\n')
        await news_file.write("\n---\n\n")

        await link_file.write(link + '\n')
        await processed_file.write(link + '\n')

        print(f"Yeni haber eklendi: {title_text} (Link: {link})")
    except Exception as e:
        print(f"Bağlantı hatası {link}: {e}")


async def fetch_and_write_news():
    try:
        async with aiofiles.open('bbc_links_2.txt', 'r') as file:
            current_links = set([line.strip() for line in await file.readlines()])
    except FileNotFoundError:
        print("'bbc_links_2.txt' dosyası bulunamadı.")
        return

    try:
        async with aiofiles.open('processed_links.txt', 'r') as file:
            processed_links = set([line.strip() for line in await file.readlines()])
    except FileNotFoundError:
        processed_links = set()

    new_links = current_links - processed_links

    if not new_links:
        print("Yeni link bulunamadı.")
        return

    async with aiohttp.ClientSession() as session:
        async with aiofiles.open('news_english.txt', 'a') as news_file, aiofiles.open('bbc_news.txt', 'a') as link_file, aiofiles.open('processed_links.txt', 'a') as processed_file:
            tasks = [process_link(session, link, news_file, link_file, processed_file) for link in new_links]
            await asyncio.gather(*tasks)


async def main():
    while True:
        await fetch_and_write_news()
        await asyncio.sleep(60)

asyncio.run(main())
