# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_prepaid_devices
import os
from selenium.webdriver.chrome.options import Options

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

today = datetime.date.today()

# get Metropcs prepaid device links
metropcs_devices_today = get_prepaid_devices('metropcs', today)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

for entry in metropcs_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make empty list of promotions
    promotions = []

    # crossed out price
    try:
        crossed_out_price = soup.find('span', class_='normal-price')
        promotions.append(['crossed out price', crossed_out_price.text.strip().replace('\n', '').replace('                                ', '.')])
    except AttributeError:
        print('no crossed out price :(')

    # make object for each promo text instance
    for promo_instance in promotions:
        entry.promo_location = promo_instance[0]
        entry.promo_text = promo_instance[1]
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

driver.quit()

