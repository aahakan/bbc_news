import asyncio
import aiohttp
from bs4 import BeautifulSoup

async def fetch_and_save_links(session):
    url = "https://www.bbc.com/news/world"

    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                latest_updates_heading = soup.find(lambda tag: tag.name == "h2" and "Latest Updates" in tag.string)

                if latest_updates_heading:
                    latest_updates_section = latest_updates_heading.find_next_sibling('div')

                    if latest_updates_section:
                        links = latest_updates_section.find_all('a', href=True)
                        new_links = set("https://www.bbc.com" + link['href'] for link in links if "https://www.bbc.co.uk/usingthebbc/terms/can-i-share-things-from-the-bbc" not in link['href'] and "{assetUri}" not in link['href'])

                        if new_links:
                            print(f"Yeni linkler bulundu: {new_links}")

                            try:
                                with open("bbc_links_2.txt", 'r+') as file:
                                    existing_links = set(line.strip() for line in file)
                                    new_links_to_add = new_links - existing_links

                                    if new_links_to_add:
                                        file.seek(0, 2)  
                                        for link in new_links_to_add:
                                            file.write(link + '\n')
                                            print(f"Yeni link eklendi: {link}")
                            except FileNotFoundError:
                                with open("bbc_links_2.txt", 'w') as file:
                                    for link in new_links:
                                        file.write(link+'\n')
                    else:
                        print("Latest Updates altındaki içerik bulunamadı.")
                else:
                    print("Latest Updates başlığı bulunamadı.")
            else:
                print(f"Sayfa yüklenemedi. Durum Kodu: {response.status}")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            await fetch_and_save_links(session)
            await asyncio.sleep(60)

asyncio.run(main())
