from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
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

# Используем Selenium для загрузки страницы и ожидания загрузки всех изображений
driver = webdriver.Chrome()
driver.get("https://www.espncricinfo.com/series/west-indies-vs-bangladesh-2024-25-1433357/fan-ratings/1")

# Прокручиваем страницу вниз, чтобы загрузить все изображения
body = driver.find_element(By.TAG_NAME, "body")
for _ in range(10):  # Прокручиваем страницу вниз несколько раз
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)  # Ждем, чтобы изображения успели загрузиться

# Ждем, пока все изображения загрузятся
WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
)

# Теперь можно парсить страницу с помощью BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Получаем очищенные данные
user_data = get_clear_data(soup)

# Выводим данные в консоль
print(json.user_data)

# Сохраняем данные в файл JSON
with open('user_data.json', 'w', encoding='utf-8') as f:
    json.dump(user_data, f, ensure_ascii=False, indent=4)