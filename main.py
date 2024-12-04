import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def get_clear_data(soup: BeautifulSoup) -> list:
    div_tag = soup.find("div", class_="ds-p-0 ds-text-right ds-overflow-x-auto ds-scrollbar-hide")
    user_data = []
    
    if div_tag:
        tbody_tag = div_tag.find("tbody")
        
        if tbody_tag:
            for row in tbody_tag.find_all("tr"):
                columns = row.find_all("td")
                
                if len(columns) > 0:
                    first_td = columns[0]

                    img_tag = first_td.find("img")
                    photo_url = img_tag.get('data-src') if img_tag and "data-src" in img_tag.attrs else img_tag.get('src')

                    id_tag = first_td.find("div", class_="ds-flex ds-flex-row ds-items-center ds-self-stretch")
                    id_tag = id_tag.find("span") if id_tag else None

                    a_tag = first_td.find("a", class_="ds-inline-flex ds-items-start ds-leading-none")
                    
                    user = {
                        "id": id_tag.text.strip() if id_tag else None,
                        "photo": photo_url if photo_url else None,
                        "name": a_tag.find("span").text.strip() if a_tag else None,
                        "Team": columns[1].text.strip(),
                        "Fan Rating": columns[2].text.strip(),
                        "Mat": columns[3].text.strip()
                    }
                    
                    user_data.append(user)
            
            return user_data
        else:
            print("Тег <tbody> не найден")
    else:
        print("Тег <div> не найден")
    
    return []

async def get_user_data(http_client: aiohttp.ClientSession, slug: str) -> dict:
    url = f"https://www.espncricinfo.com/series/{slug}/fan-ratings/1"
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'accept': '*/*'
    }
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')


    # Используем Selenium для загрузки страницы и ожидания загрузки всех изображений
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):  
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)  

  
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
    )


    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    user_data = get_clear_data(soup)

    # Выводим данные в консоль
    for user in user_data:
        print(user)

    # Сохраняем данные в файл JSON

async def main():
    async with aiohttp.ClientSession() as session:
        slug = "west-indies-vs-bangladesh-2024-25-1433357"
        await get_user_data(session, slug)

if __name__ == "__main__":
    asyncio.run(main())