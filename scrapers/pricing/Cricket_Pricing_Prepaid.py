# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
import os
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
from scrapers.promotions.Cricket_Promotions_Prepaid import cri_scrape_prepaid_promotions
import datetime


def price_parser(string):
    string = string.strip()
    string = string.replace("$", "")
    string = string.replace("*", "")
    string = string.replace("FREE", "0.00")
    return string

def cri_scrape_prepaid_smartphone_prices():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # go to website
    driver.get("https://www.cricketwireless.com/cell-phones/smartphones")
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'cricket'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    # iterate through devices
    for div in soup.findAll('div', {'class':'row picAndPriceWrapper'}):
        if div.find('span', {'class': 'extraHeaderText'}).text.lower().find('pre-owned') == -1:
            scraped_prepaid_price.device = remove_colors(div.find("a", {'class': 'headline-link'}).text).strip()
            scraped_prepaid_price.url = "https://www.cricketwireless.com" + div.find("a", {'class': 'headline-link'})["href"]

            was_price = div.find('div', class_='price was-price')
            scraped_prepaid_price.list_price = price_parser(was_price.text)

            try:
                current_price = div.find('div', class_='price current-price')
                scraped_prepaid_price.retail_price = price_parser(current_price.text)
            except AttributeError:
                scraped_prepaid_price.retail_price = price_parser(was_price.text)

            # go to url
            driver.get(scraped_prepaid_price.url)
            time.sleep(2)
            html = driver.page_source
            price_soup = BeautifulSoup(html, "html.parser")

            # if GB in device name, remove it and get storage size from there
            if 'GB' in scraped_prepaid_price.device:
                storage = scraped_prepaid_price.device.split(' ')[-1]
                device_name = scraped_prepaid_price.device.replace(storage, '').strip()
                storage = storage.replace('GB', '')
                scraped_prepaid_price.device = device_name
            if scraped_prepaid_price.device.find("(") != -1:
                storage = scraped_prepaid_price.device.split(" ")[-1]
                device_name = scraped_prepaid_price.device.replace(storage, "").strip()
                storage = storage.replace("(", "").replace(")", "")
                scraped_prepaid_price.device = device_name

            # if GB not in device name, find it on the page
            elif price_soup.findAll('div', class_='specs3 parbase richtext'):
                storage = price_soup.findAll('div', class_='specs3 parbase richtext')[0]
                if ',' in storage.text:
                    storage = storage.text.split(',')
                    if 'ROM' in storage[1]:
                        storage = storage[1]
                    elif 'ROM' in storage[0]:
                        storage = storage[0]
                    storage = storage.split('GB', 2)[0]
                    storage = storage.replace("up to ", "")
                    storage = storage.strip()
                elif 'RAM' in storage.text:
                    storage = storage.text.split('GB RAM')[1]
                    storage = storage.split('GB ROM')[0]
                    storage = storage.strip()
                else:
                    storage = storage.text.split('GB', 2)[0]
                    storage = storage.replace("Up to ", "")
                    storage = storage.strip()
            scraped_prepaid_price.storage = storage

            remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                     scraped_prepaid_price.storage, scraped_prepaid_price.date)
            add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                            scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                            scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                            scraped_prepaid_price.date, scraped_prepaid_price.time)

            cri_scrape_prepaid_promotions(driver, scraped_prepaid_price.url, scraped_prepaid_price.device,
                                          scraped_prepaid_price.storage)

    driver.close()

