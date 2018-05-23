# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_prepaid_devices, add_scraped_promotions_to_database
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# time variables
date = datetime.date.today()
time_now = datetime.datetime.now().time()

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
    try:
        sale_price = driver.find_element_by_xpath('//*[@id="pricingWrapper"]/div[1]/div[1]')
        promotions.append(['sale price', sale_price.text.strip().replace('\n', '').replace('                           ', '')])
    except NoSuchElementException:
        print('no sale price')

    # make object for each promo text instance
    for promo_instance in promotions:
        entry.promo_location = promo_instance[0]
        entry.promo_text = promo_instance[1]
        entry.date = date
        entry.time = time_now
        entry.provider = 'cricket'
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)
        add_scraped_promotions_to_database(entry.provider, entry.device_name, entry.device_storage,
                                           entry.promo_location, entry.promo_text, entry.url, entry.date, entry.time)

driver.quit()

