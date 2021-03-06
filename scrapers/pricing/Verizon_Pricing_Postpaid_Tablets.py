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
import pyautogui


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
    string = string.replace("Motorola", "")
    string = string.replace('Kyocera', 'Kyocera ')
    string = string.replace("Apple", "")
    string = string.replace("E4", "e4")
    string = string.replace("  ", " ")
    string = string.replace(" Black", "")
    string = string.replace(" Space Gray", "")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    string = remove_non_ascii(string)
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
    string = string.replace('galaxy tab a (8.0 inch)', 'galaxy tab a')
    string = string.strip()
    return string


def monthly_price_parser(string):
    string = str(string)
    string = string.split('/mo.')[0]
    string = string.replace('$', '')
    return string

def retail_price_parser(string):
    string = str(string)
    string = string.replace('Retail Price', '')
    string = string.split('was')[0]
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
    driver.implicitly_wait(5)

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

    # get device names and links from the tablet landing page
    for device in soup.findAll('div', class_='cursorPointer pad15 onlySidePad tile background_supporting border_CC'):

        device_contents = device.find('a')
        scraped_postpaid_price.device = brandparser(device_contents.text)
        if scraped_postpaid_price.device.find("pre-owned") != -1:
            continue
        scraped_postpaid_price.url = 'https://www.verizonwireless.com' + device_contents["href"]

        promo_text = device.find('div', class_='offer-text').text
        if promo_text != '':
            add_scraped_promotions_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                               '0', 'device landing page', promo_text,
                                               scraped_postpaid_price.url, scraped_postpaid_price.date,
                                               scraped_postpaid_price.time)

        # go to url
        driver.get(scraped_postpaid_price.url)
        time.sleep(5)
        html = driver.page_source
        device_soup = BeautifulSoup(html, "html.parser")
        site_title = device_soup.find_all("title")
        if not site_title or site_title[0] == "<title></title>":
            continue

        else:
            # select each device size
            size_button_pad = device_soup.find('div', class_='displayFlex rowNoWrap priceSelectorRow')
            size_buttons = size_button_pad.findAll('div', class_='grow1basis0 priceSelectorColumn radioGroup positionRelative')
            for size_button_number in range(1, len(size_buttons) + 1):

                # record new device size
                scraped_postpaid_price.storage = size_buttons[size_button_number - 1].text.replace('GB', '')

                # remove popup before clicking
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(
                            size_button_number) + ']/div/div/p').click()
                except WebDriverException:
                    driver.find_element_by_link_text('×').click()
                    driver.find_element_by_xpath(
                        '//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(
                            size_button_number) + ']/div/div/p').click()

                # click on different storage size to show device size-specific promos
                time.sleep(2)
                html = driver.page_source
                device_soup = BeautifulSoup(html, "html.parser")

                values_list = device_soup.findAll('div', class_='sizePad')
                scraped_postpaid_price.monthly_price = monthly_price_parser(values_list[-3].text)
                scraped_postpaid_price.contract_ufc = contract_ufc_parser(values_list[-2].text.replace(',', ''))
                scraped_postpaid_price.retail_price = retail_price_parser(values_list[-1].text.replace(',', ''))

                # remove storage from device name if it is in it
                if scraped_postpaid_price.storage in scraped_postpaid_price.device:
                    scraped_postpaid_price.device = scraped_postpaid_price.device.replace(
                        scraped_postpaid_price.storage + 'gb', '')

                remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                          scraped_postpaid_price.storage, scraped_postpaid_price.date)
                add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                         scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                         scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                         scraped_postpaid_price.date, scraped_postpaid_price.time)

                ver_scrape_postpaid_promotions(device_soup, driver, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                               scraped_postpaid_price.storage)

    driver.close()



