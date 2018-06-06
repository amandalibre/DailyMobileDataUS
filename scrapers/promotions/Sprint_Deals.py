# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion
from scrapers.scraper_functions.util import fullpage_screenshot

def spr_scrape_deals_page():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.sprint.com/')
    time.sleep(5)

    # go to Phones url (since url could change)
    driver.find_element_by_link_text('Deals').click()
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # change header css
    nav = driver.find_element_by_css_selector('body > div.sprint-app > header')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav)

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\spr_deals_' + today + '.png')

    # make promotions object
    scraped_promotion = ScrapedPromotion()

    # hard coded variables
    scraped_promotion.provider = 'sprint'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.device_storage = '0'
    scraped_promotion.promo_location = 'deals page'
    scraped_promotion.url = driver.current_url

    for div in soup.findAll('div', class_='ui-bucket__content'):
        deals_page_promo = div.text.strip().replace('\n', '')
        scraped_promotion.promo_text = deals_page_promo
        print(scraped_promotion.provider, scraped_promotion.device_name,  scraped_promotion.device_storage,
              scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
              scraped_promotion.date, scraped_promotion.time)
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)
    driver.quit()




