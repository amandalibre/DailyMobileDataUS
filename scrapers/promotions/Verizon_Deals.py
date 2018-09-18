# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion


def ver_scrape_deals_page():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # go to website
    driver.get("https://www.verizonwireless.com/promos/")
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_promotion = ScrapedPromotion()

    # hardcoded variables
    scraped_promotion.provider = 'verizon'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.promo_location = 'deals page'
    scraped_promotion.device_storage = '0'
    scraped_promotion.url = driver.current_url

    # get deals
    for div in soup.findAll('div', class_='Container'):
        if div.text.strip().replace('\n', '') != '':
            deals_page_promo = div.text.strip().replace('\n', '')
            scraped_promotion.promo_text = deals_page_promo
            print(scraped_promotion.provider, scraped_promotion.device_name,  scraped_promotion.device_storage,
                  scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
                  scraped_promotion.date, scraped_promotion.time)
            add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                               scraped_promotion.device_storage, scraped_promotion.promo_location,
                                               scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                               scraped_promotion.time)
    driver.close()






