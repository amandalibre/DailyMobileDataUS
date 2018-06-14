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
    if "(" in string:
        if string.split('(')[1] != 'AT&T Certified Restored)':
            string = string.split('(')[0]
    string = remove_colors(string)
    return string

def price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    return string

def get_link(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    string = "https://www.att.com" + string
    return string

def att_scrape_prepaid_smartphone_prices():
    # headless Chrome
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

    # use keyboard shortcut to activate Full Page Screen Capture extension
    pyautogui.hotkey('alt', 'shift', 'p')
    time.sleep(10)

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # hardcoded variables
    scraped_prepaid_price.provider = 'att'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

    att_dict = {}
    count = 0
    for div in soup.findAll('div', class_='list-title'):
        att_dict[count] = {'link': get_link(div.contents)}
        for a in div.findAll('a', class_='titleURLchng'):
            device_name = device_parser(a.text)
            att_dict[count].update({'device_name': device_name.strip()})
            count += 1

    count1 = 0
    for div in soup.findAll('div', class_='listPrice orangeFontStyle marginTop38'):
        att_dict[count1].update({'price': price_parser(div.text)})
        att_dict[count1].update({'retail_price': price_parser(div.text)})
        count1 += 1

    if count != count1:
        print('For loop counts are different. Program stopped.')

    for device in range(len(att_dict)):
        if 'AT&T Certified Restored' not in att_dict[device]['device_name'] \
                and 'LG B470' not in att_dict[device]['device_name']:

            # record device name, url and prices
            scraped_prepaid_price.device = att_dict[device]['device_name']
            scraped_prepaid_price.url = att_dict[device]['link']
            scraped_prepaid_price.retail_price = att_dict[device]['retail_price']
            scraped_prepaid_price.list_price = att_dict[device]['price']

            driver.get(scraped_prepaid_price.url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # get device size
            if scraped_prepaid_price.device == 'Galaxy Express Prime 3':
                scraped_prepaid_price.storage = '16'
            elif soup.find(id='putMemoryHere'):
                span = soup.find(id='putMemoryHere')
                scraped_prepaid_price.storage = span.text.replace('GB', '')
            elif soup.findAll('div', class_='tiny-accordion ng-isolate-scope'):
                memory = soup.findAll('div', class_='tiny-accordion ng-isolate-scope')[0]
                for div in memory.findAll('div', class_='span9 description')[15]:
                    storage = div.strip()
                    scraped_prepaid_price.storage = storage.replace('Up to ', '')
            else:
                for next in soup.findAll('div', class_='fltLIco'):
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



