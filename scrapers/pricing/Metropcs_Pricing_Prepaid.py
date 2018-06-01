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

def price_parser(string):
    string = string.replace("00", ".00")
    string = string.replace("$", "")
    return string

def link_parser(string):
    string = str(string)
    string = string.split('pdl_track_phone_title_click="', 1)[1]
    string = string.split('"', 1)[0]
    string = string.replace('| ', '/')
    string = string.replace(' ', '-')
    string = 'https://www.metropcs.com/shop/phones/details/' + string
    return string

def met_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get("https://www.metropcs.com/shop/phones")
    time.sleep(15)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'metropcs'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    metropcs_dict = {}
    count = 0
    for span in soup.findAll("span", class_="cursor"):
        metropcs_dict[count] = {'device_name': remove_colors(span.text).strip(), 'link': link_parser(span)}
        count += 1

    count1 = 0
    for div in soup.findAll("div", class_="card-content card-price"):
        if "After all offers" in div.text:
            for span in div("span", class_="current-price"):
                metropcs_dict[count1].update({'price': price_parser(span.text.replace('\n', ''))})
            for span in div("span", class_="normal-price"):
                metropcs_dict[count1].update({'retail_price': price_parser(span.text.replace('\n', ''))})
            count1 += 1
        else:
            for span in div("span", class_="current-price"):
                metropcs_dict[count1].update({'price': price_parser(span.text.replace('\n', ''))})
                metropcs_dict[count1].update({'retail_price': price_parser(span.text.replace('\n', ''))})
            count1 += 1

    if count != count1:
        print('For loop counts are different. Program stopped.')

    for device in range(len(metropcs_dict)):
        if 'Hotspot' not in metropcs_dict[device]['device_name'] and 'SIM' not in metropcs_dict[device]['device_name']:

            # set device name, url and prices
            scraped_prepaid_price.device = metropcs_dict[device]['device_name']
            scraped_prepaid_price.url = metropcs_dict[device]['link']
            scraped_prepaid_price.retail_price = metropcs_dict[device]['retail_price']
            scraped_prepaid_price.list_price = metropcs_dict[device]['price']

            # go to url
            driver.get(scraped_prepaid_price.url)
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # one hardcoded exception
            if scraped_prepaid_price.device == 'HTC Desire 530':
                scraped_prepaid_price.storage = '16'

            # if storage size in device name, update device name and add set storage size
            elif metropcs_dict[device]['device_name'].find('GB') != -1:
                storage = scraped_prepaid_price.device.split(' ')[-1]
                scraped_prepaid_price.device = scraped_prepaid_price.device.replace(storage, '').strip()
                scraped_prepaid_price.storage = storage.replace('GB', '')

            # for devices with specs preview wrapper under header
            elif 'storage' not in metropcs_dict[device]:
                for p in soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        scraped_prepaid_price.storage = p.text.split(' ')[0].replace('GB', '')
                        break
                if 'storage' not in metropcs_dict[device]:
                    for span in soup.findAll('span', class_='p-l-5 v-align-super'):
                        if 'GB' in span.text:
                            scraped_prepaid_price.storage = span.text.split(' ')[0].replace('GB', '')
                            break
            elif 'storage' not in metropcs_dict[device]:
                for p in soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        scraped_prepaid_price.storage = p.text.split(' ')[0].replace('GB', '')
                        break

            remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                     scraped_prepaid_price.storage, scraped_prepaid_price.date)
            add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                            scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                            scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                            scraped_prepaid_price.date, scraped_prepaid_price.time)

            met_scrape_prepaid_promotins(soup, scraped_prepaid_price.url, scraped_prepaid_price.device,
                                         scraped_prepaid_price.storage)


    driver.close()


