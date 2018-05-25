# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def brandparser(string):
    string = string.replace("\n", "")
    string = string.replace("Google", "")
    string = string.replace("Samsung", "")
    string = string.replace("MOTO", "Moto")
    string = string.replace("LG", "LG ")
    string = string.replace("ZTE", "ZTE ")
    string = string.replace("HTC", "HTC ")
    string = string.replace("Optimus ", "")
    string = string.replace("Apple", "")
    string = string.replace('ASUS', 'ASUS ')
    string = string.replace("Prepaid", "")
    string = string.replace(", Phone by", "")
    string = string.replace("with Sapphire Shield", "")
    string = string.replace("Google", "")
    string = string.replace("Samsung", "")
    string = string.replace("HTC", "HTC ")
    string = string.replace("Motorola", "")
    string = string.replace('Kyocera', 'Kyocera ')
    string = string.replace("Apple", "")
    string = string.replace("E4", "e4")
    string = string.replace("  ", " ")
    string = string.replace(" Black", "")
    string = string.replace(" Space Gray", "")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    string = removeNonAscii(string)
    string = string.strip()
    string = string.replace('Galaxy Tab E', 'Galaxy Tab E 8')
    if string == 'iPad 9.7':
        string = 'iPad 9.7 (2018)'
    if string == '10.5-inch iPad Pro':
        string = 'iPad Pro 10.5'
    if string == '12.9-inch iPad Pro':
        string = 'iPad Pro 12.9'
    if string == 'iPad':
        string = 'iPad 9.7 (2018)'
    string = string.lower()
    string = string.replace('z10', '10')
    string = string.replace('z8s', '8s')
    string = string.strip()
    string = string.replace('12.9-inch ipad pro', 'ipad pro 12.9')
    string = string.replace('10.5-inch ipad pro', 'ipad pro 10.5')
    return string

def link_parser(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    return string

def monthly_price_parser(string):
    string = str(string)
    string = string.split('/mo.')[0]
    string = string.replace('$', '')
    return string

def retail_price_parser(string):
    string = str(string)
    string = string.replace('Retail Price', '')
    string = string.replace('$', '')
    return string

def contract_ufc_parser(string):
    string = str(string)
    string = string.split('was')[0]
    string = string.replace('$', '')
    string = string.strip()
    string = string.replace('2-Year Contract', '')
    string = string.replace('-Year Contract', '')
    return string


def ver_scrape_postpaid_tablet_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # go to website
    driver.get("https://www.verizonwireless.com/tablets/")
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_postpaid_price = ScrapedPostpaidPrice()

    # hardcoded variables
    scraped_postpaid_price.provider = 'verizon'
    scraped_postpaid_price.date = datetime.date.today()
    scraped_postpaid_price.time = datetime.datetime.now().time()

    ver_postpaid_dict = {}

    # get device names and links from the tablet landing page
    count = 0
    for div in soup.findAll('div', class_='cursorPointer pad15 onlySidePad tile background_supporting border_CC'):
        for a in div.findAll('a'):
            ver_postpaid_dict[count] = {'device_name': brandparser(a.text)}
            ver_postpaid_dict[count].update({'url': 'https://www.verizonwireless.com' + link_parser(a)})
            break
        count += 1

    # go to each device's page to get the pricing details
    for device in range(len(ver_postpaid_dict)):
        if 'certified pre-owned' not in ver_postpaid_dict[device]['device_name']:

            # record device name and url
            scraped_postpaid_price.device = ver_postpaid_dict[device]['device_name']
            scraped_postpaid_price.url = ver_postpaid_dict[device]['url']

            # go to url
            driver.get(ver_postpaid_dict[device]['url'])
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            values_list = soup.findAll('div', class_='sizePad')
            scraped_postpaid_price.storage = values_list[0].text.replace('GB', '')
            scraped_postpaid_price.monthly_price = monthly_price_parser(values_list[-3].text)
            scraped_postpaid_price.contract_ufc = contract_ufc_parser(values_list[-2].text.replace(',', ''))
            scraped_postpaid_price.retail_price = retail_price_parser(values_list[-1].text.replace(',', ''))

            # remove storage from device name if it is in it
            if scraped_postpaid_price.storage in scraped_postpaid_price.device:
                scraped_postpaid_price.device = scraped_postpaid_price.device.replace(scraped_postpaid_price.storage + 'gb', '')

            # print device info
            print(scraped_postpaid_price.device, scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                  scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                  scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url)

            # add to database
            remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                      scraped_postpaid_price.storage, scraped_postpaid_price.date)
            add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                     scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                     scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                     scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                     scraped_postpaid_price.date, scraped_postpaid_price.time)

    driver.close()


ver_scrape_postpaid_tablet_prices()

