# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_prepaid_devices
import os
from selenium.webdriver.chrome.options import Options

# time variables
date = datetime.date.today()
time = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# get Cricket prepaid device links
cricket_devices_today = get_prepaid_devices('cricket', date)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

for entry in cricket_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make empty list of promotions
    promotions = []

    # sale price
    sale_price = soup.find('div', class_='sale-price-wrapper')
    promotions.append(['sale price', sale_price.text.strip().replace('\n', '').replace('                           ', '')])

    # make object for each promo text instance
    for promo_instance in promotions:
        entry.promo_location = promo_instance[0]
        entry.promo_text = promo_instance[1]
        entry.date = date
        entry.time = time
        entry.provider = 'cricket'
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

driver.quit()

