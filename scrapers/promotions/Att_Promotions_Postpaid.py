# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_postpaid_devices, add_scraped_promotions_to_database
from selenium.webdriver.chrome.options import Options
import os

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# time variables
date = datetime.date.today()
time_now = datetime.datetime.now().time()

def att_get_device_links():
    # get at&t postpaid device links
    att_devices_today = get_postpaid_devices('att', date)

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    for entry in att_devices_today:
        driver.get(entry.url)
        time.sleep(8)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # make empty list of promotions
        promotions = []

        # upper banner text
        for span in soup.findAll("span", class_="offerTxt"):
            if span.text.strip() != '':
                upper_banner_text = span.text.strip()
                promotions.append(['upper banner', upper_banner_text])

        # lower banner text
        for div in soup.findAll("div", class_="ds2MarketingMessageTextStyle"):
            promotions.append(['lower banner', div.text])

        # make object for each promo text instance
        for promo_instance in promotions:
            entry.promo_location = promo_instance[0]
            entry.promo_text = promo_instance[1]
            entry.date = date
            entry.time = time_now
            entry.provider = 'att'
            print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)
            add_scraped_promotions_to_database(entry.provider, entry.device_name, entry.device_storage,
                                               entry.promo_location, entry.promo_text, entry.url, entry.date, entry.time)

    driver.quit()


att_get_device_links()