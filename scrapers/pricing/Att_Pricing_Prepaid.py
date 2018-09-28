# -*- coding: utf-8 -*-
import datetime
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, \
    remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
import pyautogui


def device_parser(string):
    string = str(string)
    string = string.strip()
    string = string.replace('- AT&T PREPAID ', '')
    string = string.replace(' - AT&T PREPAID', '')
    if string.find("($") != -1:
        string = string.split("(")[0]
    string = remove_colors(string)
    string = string.strip()
    return string


def price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    return string


def att_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get("https://www.att.com/shop/wireless/devices/prepaidphones.html")
    time.sleep(10)

    # check if all devices are shown on page
    devices_shown = driver.find_element_by_class_name('deviceCount').text.split(' ')[-1]
    devices_total = driver.find_element_by_class_name('deviceSize').text
    if devices_shown != devices_total:
        # click 'Show All' button if it exists
        if driver.find_element_by_id("deviceShowAllLink"):
            driver.find_element_by_id("deviceShowAllLink").click()

    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # hardcoded variables
    scraped_prepaid_price.provider = 'att'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    # iterate through devices
    for device in soup.findAll("div", {"class": "list-item"}):

        device_contents = device.find("a", {"class": "titleURLchng"})

        scraped_prepaid_price.device = device_parser(device_contents.text)
        if scraped_prepaid_price.device.find("Restored") != -1 or scraped_prepaid_price.device.find("Flip") != -1 \
                or scraped_prepaid_price.device.find("Pre-Owned") != -1 or scraped_prepaid_price.device.find(
                "B4700") != -1:
            continue

        scraped_prepaid_price.url = "https://www.att.com" + device_contents["href"]

        scraped_prepaid_price.list_price = price_parser(
            device.find('div', class_='listPrice orangeFontStyle marginTop38').text)
        scraped_prepaid_price.retail_price = scraped_prepaid_price.list_price

        # go to device url
        driver.get(scraped_prepaid_price.url)
        html = driver.page_source
        device_soup = BeautifulSoup(html, "html.parser")

        # get device size
        if scraped_prepaid_price.device == 'Galaxy Express Prime 3' \
                or scraped_prepaid_price.device == 'LG Phoenix Plus' or scraped_prepaid_price.device == 'Alcatel TETRA':
            scraped_prepaid_price.storage = '16'
        elif scraped_prepaid_price.device == 'ZTE Blade Spark':
            scraped_prepaid_price.storage = '7'
        elif device_soup.find(id='putMemoryHere'):
            span = device_soup.find(id='putMemoryHere')
            scraped_prepaid_price.storage = span.text.replace('GB', '')
        elif device_soup.findAll('div', class_='tiny-accordion ng-isolate-scope'):
            memory = device_soup.findAll('div', class_='tiny-accordion ng-isolate-scope')[0]
            for div in memory.findAll('div', class_='span9 description')[15]:
                storage = div.strip()
                if storage.find("Up to") == -1:
                    storage = memory.findAll('div', class_='span9 description')[21]
                    storage = storage.strip()
                scraped_prepaid_price.storage = storage.replace('Up to ', '')
        else:
            for next in device_soup.findAll('div', class_='fltLIco'):
                if 'GB' in next.text:
                    storage = next.text.strip()
                    scraped_prepaid_price.storage = storage.split(' ')[-1].replace('GB', '')
                    break

        # remove GB from storage
        if 'GB' in scraped_prepaid_price.storage:
            scraped_prepaid_price.storage = scraped_prepaid_price.storage.replace('GB', '')

        remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                 scraped_prepaid_price.storage, scraped_prepaid_price.date)
        add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                        scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                        scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                        scraped_prepaid_price.date, scraped_prepaid_price.time)

    driver.close()


