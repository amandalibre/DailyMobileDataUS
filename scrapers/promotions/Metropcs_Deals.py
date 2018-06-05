# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.model.Scraped_Promotion import ScrapedPromotion
from data.database.Database_Methods import add_scraped_promotions_to_database
from scrapers.scraper_functions.util import fullpage_screenshot


def met_scrape_deals_page():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.metropcs.com/shop/deals')
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_promotion = ScrapedPromotion()

    # set hardcoded variables
    scraped_promotion.provider = 'metropcs'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.device_storage = '0'
    scraped_promotion.device_name = 'N/A'
    scraped_promotion.url = driver.current_url
    scraped_promotion.promo_location = 'deals page'

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\met_deals_' + today + '.png')

    # get first banner
    for div in soup.findAll('div', class_='col-md-12 col-xs-12 p-t-30-lg p-t-10-md text-left'):
        deals_page_promo = div.text.strip().replace('\n', '')
        scraped_promotion.promo_text = deals_page_promo
        print(scraped_promotion.provider, scraped_promotion.device_name, scraped_promotion.device_storage,
              scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
              scraped_promotion.date, scraped_promotion.time)
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)

    # get promotions
    for div in soup.findAll('div', class_=' col-xs-12 col-sm-6'):
        for div1 in div.findAll('div', class_='m-b-10'):
            deals_page_promo = div1.a.img['alt']
            scraped_promotion.promo_text = deals_page_promo
            print(scraped_promotion.provider, scraped_promotion.device_name, scraped_promotion.device_storage,
                  scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
                  scraped_promotion.date, scraped_promotion.time)
            add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                               scraped_promotion.device_storage, scraped_promotion.promo_location,
                                               scraped_promotion.promo_text, scraped_promotion.url,
                                               scraped_promotion.date,
                                               scraped_promotion.time)

    driver.close()


met_scrape_deals_page()