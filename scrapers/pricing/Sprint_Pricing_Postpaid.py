# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from scrapers.promotions.Sprint_Promotions_Postpaid import spr_scrape_postpaid_promotions
import pyautogui

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def device_parser(string):
    string = str(string)
    string = string.replace("³", "3")
    string = string.replace("⁵", "5")
    string = string.replace("⁴", "4")
    string = string.replace("²", "2")
    string = removeNonAscii(string)
    string = string.replace('plus', 'Plus')
    string = string.replace('Motorola Moto Z Force Edition 2nd Gen', 'Moto Z2 Force Edition')
    string = string.replace('Motorola Moto E 4th Gen', 'Moto e4')
    string = string.replace(' - Exclusively at Sprint', '')
    string = string.replace('Samsung ', '')
    string = string.replace('Apple ', '')
    string = string.lower()
    string = string.replace('motorola e5 plus', 'moto e5 plus')
    string = string.replace('lg g7 thinq pre-order', 'lg g7 thinq')
    return string

def price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    string = string.split('/')[0]
    if '\n' in string:
        string = string.split('\n')[1]
    return string


def spr_get_prices(soup, scraped_postpaid_price):

    # initialize price variables
    scraped_postpaid_price.monthly_price = '0.00'
    scraped_postpaid_price.retail_price = '0.00'
    scraped_postpaid_price.onetime_price = '0.00'

    # get prices
    for label in soup.findAll('label', class_='soar-selection__label'):
        if label.find('strong').text == ' Sprint Flex 18-mo. lease':
            monthly = label.findAll('span', class_='display-block')
            scraped_postpaid_price.monthly_price = price_parser(monthly[0].text.strip())
            scraped_postpaid_price.onetime_price = price_parser(monthly[1].text.strip())
        if label.find('strong').text == ' Full price':
            retail = label.findAll('span', class_='display-block')
            scraped_postpaid_price.retail_price = price_parser(retail[1].text.strip().replace(',', ''))

    return scraped_postpaid_price


def spr_scrape_postpaid_smartphone_prices():
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

    pricing_errors = []

    # go to website
    driver.get('https://www.sprint.com/en/shop/cell-phones.html')
    time.sleep(5)

    # # go to Phones url (since url could change)
    driver.find_element_by_xpath('/html/body/div[1]/header/div[2]/div/div/div[1]/nav/ul/li[3]/a').click()
    time.sleep(1)
    driver.find_element_by_link_text('All phones').click()
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # use keyboard shortcut to activate Full Page Screen Capture extension
    pyautogui.hotkey('alt', 'shift', 'p')
    time.sleep(13)

    # make scraper object
    scraped_postpaid_price = ScrapedPostpaidPrice()

    # set hardcoded variables
    scraped_postpaid_price.provider = 'sprint'
    scraped_postpaid_price.date = datetime.date.today()
    scraped_postpaid_price.time = datetime.datetime.now().time()

    # make dictionary of devices on landing page
    spr_postpaid_dict = {}

    count = 0
    for li in soup.findAll('li', class_='col-xs-24 col-sm-12 col-lg-8 text-center device-tile'):
        for a in li.findAll('a'):
            if '/en/shop/' in a['href']:
                spr_postpaid_dict[count] = {'url': 'https://www.sprint.com' + a['href']}
        for h3 in li.findAll('h3', class_='font-size-18 line-height-24 font-normal my-0'):
            spr_postpaid_dict[count].update({'device_name': device_parser(h3.text)})
        try:
            promo_text = li.find('span', class_='color--purple font-size-14').text.strip()
        except AttributeError:
            promo_text = ''
        if promo_text != '' and 'pre-owned' not in spr_postpaid_dict[count]['device_name'] and \
              'linelink' not in spr_postpaid_dict[count]['device_name'] and \
              'sim' not in spr_postpaid_dict[count]['device_name'] and \
              'flip' not in spr_postpaid_dict[count]['device_name'] and \
                'xp5s' not in spr_postpaid_dict[count]['device_name'] and \
                'kyocera duraxtp' not in spr_postpaid_dict[count]['device_name'] and \
                'kyocera duratr' not in spr_postpaid_dict[count]['device_name'] and \
                'sonim xp strike' not in spr_postpaid_dict[count]['device_name'] and \
                'sonim xp5s' not in spr_postpaid_dict[count]['device_name']:
            add_scraped_promotions_to_database(scraped_postpaid_price.provider, spr_postpaid_dict[count]['device_name'],
                                               '0', 'device landing page', promo_text,
                                               spr_postpaid_dict[count]['url'], scraped_postpaid_price.date,
                                               scraped_postpaid_price.time)
        count += 1

    for device in range(len(spr_postpaid_dict)):
        if 'pre-owned' not in spr_postpaid_dict[device]['device_name'] and \
              'linelink' not in spr_postpaid_dict[device]['device_name'] and \
              'sim' not in spr_postpaid_dict[device]['device_name'] and \
              'flip' not in spr_postpaid_dict[device]['device_name'] and \
                'xp5s' not in spr_postpaid_dict[device]['device_name'] and \
                'kyocera duraxtp' not in spr_postpaid_dict[device]['device_name'] and \
                'kyocera duratr' not in spr_postpaid_dict[device]['device_name'] and \
                'sonim xp strike' not in spr_postpaid_dict[device]['device_name'] and \
                'sonim xp5s' not in spr_postpaid_dict[device]['device_name']:

            # set device name and url
            scraped_postpaid_price.device = spr_postpaid_dict[device]['device_name']
            scraped_postpaid_price.url = spr_postpaid_dict[device]['url']

            # go to url
            driver.get(scraped_postpaid_price.url)
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # check if link is correct
            if 'credit=A2&contractName=0-yr-lb-18months&deviceQuantity=1&plan=pln10820000prd' not in driver.current_url:
                driver.get(scraped_postpaid_price.url + '?credit=A2&contractName=0-yr-lb-18months&deviceQuantity=1&plan=pln10820000prd')
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

            # if 404 error, stop program
            site_title = soup.find_all("title")
            if '404' in str(site_title):
                print('404 Error: ' + spr_postpaid_dict[device]['device_name'])
                quit()

            # check to make sure device_name on page is the same as the device_name on the landing page
            device_name = device_parser(driver.find_element_by_xpath('/html/body/div[1]/article/div[3]/div[1]/div[1]/div[1]/div/div/div[1]/h1').text)
            if device_name != scraped_postpaid_price.device:
                print('Website Error: ', scraped_postpaid_price.device, ' on landing page, ', device_name, ' on individual page')
                break

            # click on drop down menu and record device sizes
            selector = driver.find_element_by_id('sprint_storage_selector')
            selector.click()
            time.sleep(2)
            sizes = selector.text.strip().replace(' GB', '')
            sizes = sizes.split('\n')

            # iterate through sizes
            for size in sizes:

                # click on size and reload page
                select = Select(driver.find_element_by_id('sprint_storage_selector'))
                select.select_by_value(size)
                time.sleep(6)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # record device size
                scraped_postpaid_price.storage = size

                # record current url
                scraped_postpaid_price.url = driver.current_url

                # check if size in specs is the same as size selected
                # in progress

                scraped_postpaid_price = spr_get_prices(soup, scraped_postpaid_price)

                # if page didn't load all the way
                if scraped_postpaid_price.onetime_price == '0.00' and scraped_postpaid_price.monthly_price == '0.00':

                    # close and reload page
                    driver.close()
                    chrome_options = Options()
                    chrome_options.add_extension("Full-Page-Screen-Capture_v3.17.crx")
                    # chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--window-size=1920x1080")
                    chrome_driver = os.getcwd() + "\\chromedriver.exe"
                    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
                    driver.get(scraped_postpaid_price.url)
                    time.sleep(5)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    spr_get_prices(soup, scraped_postpaid_price)

                    if scraped_postpaid_price.onetime_price == '0.00' and scraped_postpaid_price.monthly_price == '0.00':
                        pricing_errors.append(scraped_postpaid_price.device + ' ' + scraped_postpaid_price.storage)

                # add to database
                remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                          scraped_postpaid_price.storage, scraped_postpaid_price.date)
                add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                         scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                         scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                         scraped_postpaid_price.date, scraped_postpaid_price.time)

                spr_scrape_postpaid_promotions(soup, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                               scraped_postpaid_price.storage)

    print("Pricing Errors:", pricing_errors)

    driver.quit()


