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

def tmo_scrape_homepage():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.t-mobile.com/')
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # change header css
    nav = driver.find_element_by_css_selector('body > header')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav)

    nav2 = driver.find_element_by_css_selector('body > header > nav')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav2)

    scroll_top_top = driver.find_element_by_css_selector('body > div.scroll-top.animate-show-hide > button > span')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; bottom: 0px;')", scroll_top_top)

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\tmo_homepage_' + today + '.png')

    # make object
    scraped_promotion = ScrapedPromotion()

    # hardcoded variables
    scraped_promotion.provider = 'tmobile'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.url = driver.current_url
    scraped_promotion.device_storage = '0'
    scraped_promotion.promo_location = 'homepage'

    for div in soup.findAll('div', class_='heroContent ng-scope'):
        deals_page_promo = div.text.strip().replace('\n', '')
        scraped_promotion.promo_text = deals_page_promo
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)
        try:
            see_more_link = div.find("div", {"class": "cta"}).a["href"]
            if see_more_link[:7] == "/offers":
                driver.get("https://www.t-mobile.com" + see_more_link)
                time.sleep(2)
                html = driver.page_source
                offer_page_soup = BeautifulSoup(html, "html.parser")
                first_faq = offer_page_soup.find("div", {"class": "panel-body"}).text.strip()
                scraped_promotion.promo_text = "FIRST FAQ: " + first_faq
                add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                                   scraped_promotion.device_storage, scraped_promotion.promo_location,
                                                   scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                                   scraped_promotion.time)

        except TypeError:
            pass

    driver.quit()







