# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.model.Scraped_Promotion import ScrapedPromotion
from data.database.Database_Methods import add_scraped_promotions_to_database
from scrapers.scraper_functions.util import fullpage_screenshot

def att_scrape_deals_page():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(6)

    # go to website
    driver.get('https://www.att.com/deals/')
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # screen shot
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\att_deals_' + today + '.png')

    # make object
    scraped_promotion = ScrapedPromotion()

    # set hardcoded variables
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.provider = 'att'
    scraped_promotion.promo_location = 'deals page'
    scraped_promotion.url = driver.current_url
    scraped_promotion.device_storage = '0'

    for slideshow in soup.findAll('div', class_='content-wrapper'):
        deals_page_promo = slideshow.text.strip().replace('\n', '')
        scraped_promotion.promo_text = deals_page_promo
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)
        item_details = slideshow.find("div", {"class": "legal"})
        try:
            legal_link = "https://www.att.com/" + item_details.a["data-ajaxdata"]
            driver.get(legal_link)
            time.sleep(2)
            html = driver.page_source
            legal_soup = BeautifulSoup(html, "html.parser")
            for legal_terms in legal_soup.body.findAll("div")[1:]:
                scraped_promotion.promo_text = "LEGAL TERMS: " + legal_terms.text.strip()
                add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                                   scraped_promotion.device_storage, scraped_promotion.promo_location,
                                                   scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                                   scraped_promotion.time)
        except (KeyError, AttributeError, TypeError):
            pass

    for div in soup.findAll('div', class_='item-wrapper'):
        deals_page_promo = div.text.strip().replace('\n', '')
        scraped_promotion.promo_text = deals_page_promo
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)
        item_details = div.find("div", {"class": "legal"})
        try:
            legal_link = "https://www.att.com/" + item_details.a["data-ajaxdata"]
            driver.get(legal_link)
            time.sleep(2)
            html = driver.page_source
            legal_soup = BeautifulSoup(html, "html.parser")
            for legal_terms in legal_soup.body.findAll("div")[1:]:
                scraped_promotion.promo_text = "LEGAL TERMS: " + legal_terms.text.strip()
                add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                                   scraped_promotion.device_storage, scraped_promotion.promo_location,
                                                   scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                                   scraped_promotion.time)
        except (KeyError, AttributeError):
            pass

    driver.quit()

