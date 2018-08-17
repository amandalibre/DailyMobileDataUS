# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException
import time, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
import pyautogui

def parser(string):
    indexstart = (string.find("$"))
    indexend = (string.find("/mo"))
    string = string[indexstart+1:indexend]
    string = string.strip()
    string = string.replace("\n", "")
    string = string.replace("Starts at", "")
    string = string.strip()
    string = re.sub("[^0-9]", "", string)
    string = str(float(string)/100)
    return string

def parser2(string):
    string = string.replace("\n", "")
    string = string.replace("Starts at", "")
    string = string.strip()
    if "was" in string:
        indexstart = (string.find("was"))
        string = string[indexstart+11:indexstart+17]
    else:
        indexstart = (string.find("$"))
        string = string[indexstart+1:indexstart+7]
        string = string.strip()
    return string


def remove_non_ascii(string): return "".join(filter(lambda x: ord(x) < 128, string))


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
    string = string.replace("LG", "LG ")
    string = string.replace("Motorola", "")
    string = string.replace('Kyocera', 'Kyocera ')
    string = string.replace("Apple", "")
    string = string.replace("E4", "e4")
    string = string.replace("  ", " ")
    string = string.replace(" Black", "")
    string = string.replace(" Space Gray", "")
    string = string.replace('Galaxy J7 2nd Gen', 'Galaxy J7 (2018)')
    string = string.replace('Galaxy J3 3rd Gen', 'Galaxy J3 (2018)')
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    string = remove_non_ascii(string)
    string = string.strip()
    return string


def ver_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get("https://www.verizonwireless.com/prepaid/smartphones/")
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'verizon'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    # get links for all the device landing pages
    page_links = []
    for a in soup.findAll('a', class_='page-link')[:-1]:
        page_links.append('https://www.verizonwireless.com/prepaid/smartphones/' + a["href"])

    # iterate through devices on landing page
    for device in soup.findAll('div', class_='gridwallTile c-gridwallTile prepaidGridwallTile'):
        scraped_prepaid_price.device = brandparser(device.find("h6", {"class": "gridwallTile_deviceName"}).text)
        if scraped_prepaid_price.device.find("Pre-Owned") != -1:
            continue
        scraped_prepaid_price.url = 'https://www.verizonwireless.com' + device["data-pdpurl"]
        scraped_prepaid_price.list_price = parser2(device.find("div", {"class": "fontSize_6"}).text)
        if scraped_prepaid_price.list_price.find("$") != -1:
            scraped_prepaid_price.list_price = scraped_prepaid_price.list_price.replace('$', '')
        scraped_prepaid_price.retail_price = scraped_prepaid_price.list_price

        # go to url
        driver.get(scraped_prepaid_price.url)
        time.sleep(1)
        html = driver.page_source
        device_soup = BeautifulSoup(html, 'html.parser')

        # get device storage
        for span in device_soup.findAll('span', class_='filter-option'):
            if 'GB' in span.text:
                scraped_prepaid_price.storage = span.text.replace('GB', '')
                break

        # add to database
        remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                 scraped_prepaid_price.storage, scraped_prepaid_price.date)
        add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                        scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                        scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                        scraped_prepaid_price.date, scraped_prepaid_price.time)

    # go to every page of device landing pages (there are usually multiple pages)
    for page_link in page_links:
        driver.get(page_link)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # iterate through devices on landing page
        for device in soup.findAll('div', class_='gridwallTile c-gridwallTile prepaidGridwallTile'):
            scraped_prepaid_price.device = brandparser(device.find("h6", {"class": "gridwallTile_deviceName"}).text)
            if scraped_prepaid_price.device.find("Pre-Owned") != -1:
                continue
            scraped_prepaid_price.url = 'https://www.verizonwireless.com' + device["data-pdpurl"]
            scraped_prepaid_price.list_price = parser2(device.find("div", {"class": "fontSize_6"}).text)
            if scraped_prepaid_price.list_price.find("$") != -1:
                scraped_prepaid_price.list_price = scraped_prepaid_price.list_price.replace('$', '')
            scraped_prepaid_price.retail_price = scraped_prepaid_price.list_price

            # go to url
            driver.get(scraped_prepaid_price.url)
            time.sleep(1)
            html = driver.page_source
            device_soup = BeautifulSoup(html, 'html.parser')

            # get device storage
            for span in device_soup.findAll('span', class_='filter-option'):
                if 'GB' in span.text:
                    scraped_prepaid_price.storage = span.text.replace('GB', '')
                    break

            # add to database
            remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                     scraped_prepaid_price.storage, scraped_prepaid_price.date)
            add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                            scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                            scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                            scraped_prepaid_price.date, scraped_prepaid_price.time)

    driver.quit()


