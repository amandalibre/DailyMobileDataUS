# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
from scrapers.promotions.Metropcs_Promotions_Prepaid import met_scrape_prepaid_promotins
import pyautogui


def price_parser(string):
    string = string.replace("00", ".00")
    string = string.replace(".000", "0.00")
    string = string.replace("$", "")
    return string


def met_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # go to website
    driver.get("https://www.metropcs.com/shop/phones")
    time.sleep(15)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.close()

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'metropcs'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    # iterate through devices
    for device in soup.findAll("div", {"class": "col-md-6 m-b-10"}):

        device_contents = device.find("span", {"class": "cursor"})
        if device_contents.text.find("SIM") == -1 and device_contents.text.find("Hotspot") == -1 and \
                device_contents.find("MetroSMART Ride") == -1:

            scraped_prepaid_price.device = remove_colors(device_contents.text.strip()).strip()
            if scraped_prepaid_price.device == 'moto e plus (5th gen)':
                scraped_prepaid_price.device = 'moto e5 Plus'
                scraped_prepaid_price.storage = '32'
            if scraped_prepaid_price.device == 'moto e (4th gen)':
                scraped_prepaid_price.device = 'moto e4'
            if scraped_prepaid_price.device == 'moto e play (5th gen)':
                scraped_prepaid_price.device = 'moto e5 play'
            scraped_prepaid_price.url = "https://www.metropcs.com/shop/phones/details/" + device_contents["pdl_track_phone_title_click"].replace(" | ", "/").replace(" ", "-")

            price_contents = device.find("div", class_="card-content card-price")
            scraped_prepaid_price.list_price = price_parser(price_contents.find("span", class_="current-price").text.replace('\n', '').strip())

            try:
                scraped_prepaid_price.retail_price = price_parser(price_contents.find("span", class_="normal-price").text.replace('\n', '').strip())
            except AttributeError:
                scraped_prepaid_price.retail_price = price_parser(price_contents.find("span", class_="current-price").text.replace('\n', '').strip())

            # go to url
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_driver = os.getcwd() + "\\chromedriver.exe"
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
            driver.get(scraped_prepaid_price.url)
            time.sleep(4)
            html = driver.page_source
            price_soup = BeautifulSoup(html, "html.parser")
            driver.close()

            # one hardcoded exception
            if scraped_prepaid_price.device == 'HTC Desire 530' or scraped_prepaid_price.device == 'moto e5 play':
                scraped_prepaid_price.storage = '16'

            # if storage size in device name, update device name and add set storage size
            elif scraped_prepaid_price.device.find('GB') != -1:
                storage = scraped_prepaid_price.device.split(' ')[-1]
                scraped_prepaid_price.device = scraped_prepaid_price.device.replace(storage, '').strip()
                scraped_prepaid_price.storage = storage.replace('GB', '')

            # for devices with specs preview wrapper under header
            elif scraped_prepaid_price.storage == "N/A":
                for p in price_soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        scraped_prepaid_price.storage = p.text.split(' ')[0].replace('GB', '')
                        break
                if 'storage' not in scraped_prepaid_price.device:
                    for span in price_soup.findAll('span', class_='p-l-5 v-align-super'):
                        if 'GB' in span.text:
                            scraped_prepaid_price.storage = span.text.split(' ')[0].replace('GB', '')
                            break
            elif 'storage' not in scraped_prepaid_price.device:
                for p in price_soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        scraped_prepaid_price.storage = p.text.split(' ')[0].replace('GB', '')
                        break

            remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                     scraped_prepaid_price.storage, scraped_prepaid_price.date)
            add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                            scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                            scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                            scraped_prepaid_price.date, scraped_prepaid_price.time)

            met_scrape_prepaid_promotins(price_soup, scraped_prepaid_price.url, scraped_prepaid_price.device,
                                         scraped_prepaid_price.storage)



