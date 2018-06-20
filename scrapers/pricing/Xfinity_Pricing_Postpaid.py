# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
import pyautogui
import json
import requests
from scrapers.promotions.Xfinity_Promotions_Prepaid import xfi_scrape_prepaid_promotins


def remove_non_ascii(string): return "".join(filter(lambda x: ord(x) < 128, string))


def device_parser(string):
    string = string.lower().strip()
    string = string.replace('(product)red', '')
    string = ''.join(filter(lambda x: ord(x) < 128, string))
    if string == 'k30':
        string = 'lg k30'
    if string == 'x charge':
        string = 'lg x charge'
    if string == 'moto e play':
        string = 'moto e5 play'
    return string


def xfi_scrape_postpaid_smartphone_prices():
    chrome_options = Options()
    chrome_options.add_extension("Full-Page-Screen-Capture_v3.17.crx")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # update Extension options
    driver.get('chrome-extension://fdpohaocaechififmbbbbbknoalclacl/options.html')
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="settings-container"]/div[2]/div[3]/div/label/input').click()
    time.sleep(2)
    pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')
    driver.find_element_by_xpath('//*[@id="settings-container"]/div[2]/div[1]/div/input').send_keys('US-Daily-Screenshots')
    pyautogui.hotkey('tab')
    time.sleep(1)

    # go to website
    driver.get('https://www.xfinity.com/mobile/shop')
    time.sleep(5)

    # use keyboard shortcut to activate Full Page Screen Capture extension
    pyautogui.hotkey('alt', 'shift', 'p')
    time.sleep(15)
    driver.close()

    # scrape json
    device_page = requests.get('https://modesto-prodapi.xfinity.com/ModestoGW/api/v1.5/products?category=device&limit=24&offset=0&sortAsc=true&sortBy=rank')
    device_soup = BeautifulSoup(device_page.text, 'html.parser')
    device_json = json.loads(device_soup.text)
    for json_obj in device_json:

        # make object
        scraped_postpaid_price = ScrapedPostpaidPrice()

        # hardcoded variables
        scraped_postpaid_price.provider = 'xfinity'
        scraped_postpaid_price.date = datetime.date.today()
        scraped_postpaid_price.time = datetime.datetime.now().time()

        # scrape data
        scraped_postpaid_price.device = device_parser(json_obj['name'])

        # get description
        description = remove_non_ascii(json_obj['description'])
        print(description)

        # create dictionary of sizes
        size_dict = []
        for variant in json_obj['variants']:
            size_variant = variant['capacity'].replace('gb', '').strip()
            if size_variant in size_dict:
                break                   # ignore duplicates of the same size
            size_dict.append(size_variant)
            scraped_postpaid_price.storage = size_variant
            scraped_postpaid_price.retail_price = variant['price']
            scraped_postpaid_price.onetime_price = '0.00'
            scraped_postpaid_price.monthly_price = variant['financePrice']
            scraped_postpaid_price.contract_ufc = '0.00'
            scraped_postpaid_price.url = 'https://www.xfinity.com/mobile/shop/device/' + json_obj['slug']

            print(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                  scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                  scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                  scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                  scraped_postpaid_price.date, scraped_postpaid_price.time)

            # add to database
            remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                      scraped_postpaid_price.storage, scraped_postpaid_price.date)
            add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                     scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                     scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                     scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                     scraped_postpaid_price.date, scraped_postpaid_price.time)

            # add promotion text to databse
            xfi_scrape_prepaid_promotins(scraped_postpaid_price.url, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, description)

