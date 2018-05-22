# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_postpaid_devices
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# time variables
date = datetime.date.today()
time = datetime.datetime.now().time()

# get Verizon postpaid device links
verizon_devices_today = get_postpaid_devices('verizon', date)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

for entry in verizon_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make empty list of promotions
    promotions = []

    # upper banner text
    upper_banner_text = driver.find_element_by_class_name('pointer')
    promotions.append(['upper banner', upper_banner_text.text.strip()])

    # promotion text under price box
    try:
        banner_above_icon = soup.find('div', class_='offersPad fontSize_12 lineHeight8')
        promotions.append(['banner above device icon', banner_above_icon.text.replace('Special Offer', '').replace('See the details', '').replace('\n', '')])
    except AttributeError:
        print('no banner above device icon')

    # crossed out price
    for div in soup.findAll('div', class_='pad8 noRightPad'):
        if 'was' in div.text:
            promotions.append(['crossed out price', div.text.replace('2-Year Contract', ' 2-Year Contract').replace('24 Monthly Payments', ' 24 Monthly Payments').replace('was ', ' was')])

    # make object for each promo text instance
    for promo_instance in promotions:
        entry.promo_location = promo_instance[0]
        entry.promo_text = promo_instance[1]
        entry.date = date
        entry.time = time
        entry.provider = 'verizon'
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

driver.quit()

