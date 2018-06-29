# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.model.Scraped_Promotion import ScrapedPromotion
from data.database.Database_Methods import add_scraped_promotions_to_database
import datetime
from scrapers.scraper_functions.util import fullpage_screenshot

def format_promo_text(string):
    string = str(string)
    string = string.strip().replace('\n', '')
    return string

def cri_scrape_homepage():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.cricketwireless.com/')
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_promotion = ScrapedPromotion()

    # set hardcoded variables
    scraped_promotion.provider = 'cricket'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.promo_location = 'homepage'
    scraped_promotion.device_name = 'N/A'
    scraped_promotion.device_storage = '0'
    scraped_promotion.url = driver.current_url

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\cri_homepage_' + today + '.png')

    # get slideshow
    main = soup.find('div', class_='main')
    for div1 in main.findAll('div', class_='constrain-width-1024'):
        deals_page_promo = format_promo_text(div1.text)
        scraped_promotion.promo_text = deals_page_promo
        print(scraped_promotion.provider, scraped_promotion.device_name, scraped_promotion.device_storage,
              scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
              scraped_promotion.date, scraped_promotion.time)
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)


    driver.close()

