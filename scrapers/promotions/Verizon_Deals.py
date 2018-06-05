# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion
from scrapers.scraper_functions.util import fullpage_screenshot

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

    # change header css
    nav = driver.find_element_by_css_selector('#vzw-gn > div > nav')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav)

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\ver_deals_' + today + '.png')

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
            # add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
            #                                    scraped_promotion.device_storage, scraped_promotion.promo_location,
            #                                    scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
            #                                    scraped_promotion.time)
    driver.close()


ver_scrape_deals_page()




