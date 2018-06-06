# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import os
import datetime
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from scrapers.promotions.Verizon_Promotions_Postpaid import ver_scrape_postpaid_promotions
from scrapers.scraper_functions.util import fullpage_screenshot

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
    string = string.lower()
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

def ver_scrape_postpaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

    # go to website
    driver.get("https://www.verizonwireless.com/smartphones/")
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # change header css
    nav = driver.find_element_by_css_selector('#vzw-gn > div > nav')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav)

    nav2 = driver.find_element_by_css_selector('#content > div > div.header > div')
    driver.execute_script("arguments[0].setAttribute('style', 'position: absolute; top: 0px;')", nav2)

    # screen shot experiment
    today = str(datetime.datetime.today().date())
    fullpage_screenshot(driver, r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Screenshots\ver_postpaid_smartphones_' + today + '.png')

    # make object
    scraped_postpaid_price = ScrapedPostpaidPrice()

    # hardcoded variables
    scraped_postpaid_price.provider = 'verizon'
    scraped_postpaid_price.date = datetime.date.today()
    scraped_postpaid_price.time = datetime.datetime.now().time()

    ver_postpaid_dict = {}

    coming_soon = []
    count = 0
    for div in soup.findAll('div', class_='cursorPointer pad15 onlySidePad tile background_supporting border_CC'):
        for a in div.findAll('a'):
            ver_postpaid_dict[count] = {'device_name': brandparser(a.text)}
            ver_postpaid_dict[count].update({'url': 'https://www.verizonwireless.com' + link_parser(a)})
            break
        for div2 in div.findAll('div', class_='NHaasTX55Rg'):
            if div2.text == 'Not available with the current pricing.':
                coming_soon.append(ver_postpaid_dict[count]['device_name'])
        promo_text = div.find('div', class_='offer-text').text
        if promo_text != '' and 'certified pre-owned' not in ver_postpaid_dict[count]['device_name']:
            add_scraped_promotions_to_database(scraped_postpaid_price.provider, ver_postpaid_dict[count]['device_name'],
                                               '0', 'device landing page', promo_text,
                                               ver_postpaid_dict[count]['url'], scraped_postpaid_price.date,
                                               scraped_postpaid_price.time)
        count += 1

    for device in range(len(ver_postpaid_dict)):
        if 'certified pre-owned' not in ver_postpaid_dict[device]['device_name'] and \
                ver_postpaid_dict[device]['device_name'] not in coming_soon:

            # record device name and url
            scraped_postpaid_price.device = ver_postpaid_dict[device]['device_name']
            scraped_postpaid_price.url = ver_postpaid_dict[device]['url']

            # go to url
            driver.get(scraped_postpaid_price.url)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # select each device size
            size_button_pad = soup.find('div', class_='displayFlex rowNoWrap priceSelectorRow')
            size_buttons = size_button_pad.findAll('div', class_='grow1basis0 priceSelectorColumn radioGroup positionRelative')
            for size_button_number in range(1, len(size_buttons) + 1):
                # record new device size
                scraped_postpaid_price.storage = size_buttons[size_button_number - 1].text.replace('GB', '')

                # remove popup before clicking
                try:
                    driver.find_element_by_xpath( '//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(size_button_number) + ']/div/div/p').click()
                except WebDriverException:
                    driver.find_element_by_class_name('fsrCloseBtn').click()
                    print('popup clicked')
                    driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(size_button_number) + ']/div/div/p').click()

                # click on different storage size to show device size-specific promos
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                values_list = soup.findAll('div', class_='sizePad')
                scraped_postpaid_price.monthly_price = monthly_price_parser(values_list[-2].text)
                scraped_postpaid_price.retail_price = retail_price_parser(values_list[-1].text.replace(',', ''))

                remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                          scraped_postpaid_price.storage, scraped_postpaid_price.date)
                add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                         scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                         scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                         scraped_postpaid_price.date, scraped_postpaid_price.time)

                ver_scrape_postpaid_promotions(soup, driver, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                               scraped_postpaid_price.storage)

    driver.close()




