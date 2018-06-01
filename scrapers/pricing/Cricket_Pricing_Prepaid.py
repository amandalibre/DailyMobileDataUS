# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
from scrapers.promotions.Cricket_Promotions_Prepaid import cri_scrape_prepaid_promotions
import datetime


def get_link(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    string = "https://www.cricketwireless.com" + string
    return string

def price_parser(string):
    string = string.strip()
    string = string.replace("$", "")
    string = string.replace("*", "")
    return string

def cri_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get("https://www.cricketwireless.com/cell-phones/smartphones")
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'cricket'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()


    cricket_dict = {}
    count = 0
    for div in soup.findAll('div', class_='row picAndPriceWrapper'):
        for span in div.findAll('span', class_='extraHeaderText'):
            if span.text == 'Pre-Owned' or span.text == 'Certified Pre-Owned':
                for a in div.findAll("a", class_="headline-link"):
                    cricket_dict[count] = {'device_name': remove_colors(a.text.strip()) + ' ' + span.text, 'link': get_link(a)}
                    count += 1
            else:
                for a in div.findAll("a", class_="headline-link"):
                    cricket_dict[count] = {'device_name': remove_colors(a.text.strip()), 'link': get_link(a)}
                    count += 1

    count1 = 0
    for div in soup.findAll('div', class_='phone-price'):
        if div.findAll('div', class_='price current-price'):
            for z in div.findAll('div', class_='price current-price'):
                cricket_dict[count1].update({'price': price_parser(z.text)})
                cricket_dict[count1].update({'retail_price': price_parser(z.text)})
                count1 += 1
        else:
            for y in div.findAll('div', class_='price was-price'):
                cricket_dict[count1].update({'price': price_parser(y.text)})
                cricket_dict[count1].update({'retail_price': price_parser(y.text)})
                count1 += 1

    if count != count1:
        print('For loop counts are different. Program stopped.')

    for device in range(len(cricket_dict)):
        if 'Certified Pre-Owned' not in cricket_dict[device]['device_name']:

            # set device name, url and prices
            scraped_prepaid_price.device = cricket_dict[device]['device_name']
            scraped_prepaid_price.url = cricket_dict[device]['link']
            scraped_prepaid_price.retail_price = cricket_dict[device]['retail_price']
            scraped_prepaid_price.list_price = cricket_dict[device]['price']

            # go to url
            driver.get(scraped_prepaid_price.url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # if GB in device name, remove it and get storage size from there
            if 'GB' in cricket_dict[device]['device_name']:
                storage = cricket_dict[device]['device_name'].split(' ')[-1]
                device_name = scraped_prepaid_price.device.replace(storage, '').strip()
                storage = storage.replace('GB', '')
                scraped_prepaid_price.device = device_name

            # if GB not in device name, find it on the page
            elif soup.findAll('div', class_='specs3 parbase richtext'):
                storage = soup.findAll('div', class_='specs3 parbase richtext')[0]
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


            # remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
            #                          scraped_prepaid_price.storage, scraped_prepaid_price.date)
            # add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
            #                                 scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
            #                                 scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
            #                                 scraped_prepaid_price.date, scraped_prepaid_price.time)

            cri_scrape_prepaid_promotions(driver, scraped_prepaid_price.url, scraped_prepaid_price.device,
                                          scraped_prepaid_price.storage)

    driver.close()

