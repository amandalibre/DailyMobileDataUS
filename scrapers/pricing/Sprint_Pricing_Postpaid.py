# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from scrapers.promotions.Sprint_Promotions_Postpaid import spr_scrape_postpaid_promotions

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def device_parser(string):
    string = str(string)
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

def spr_scrape_postpaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.sprint.com/')
    time.sleep(5)

    # go to Phones url (since url could change)
    driver.find_element_by_link_text('Phones').click()
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

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
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # if 404 error, stop program
            site_title = soup.find_all("title")
            if '404' in str(site_title):
                print('404 Error: ' + spr_postpaid_dict[device]['device_name'])
                quit()

            # click on each device size and record it as device_storage
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
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # record device size
                scraped_postpaid_price.storage = size

                # get prices
                for label in soup.findAll('label', class_='soar-selection__label'):
                    if label.find('strong').text == ' Sprint Flex 18-mo. lease':
                        monthly = label.findAll('span', class_='display-block')
                        scraped_postpaid_price.monthly_price = price_parser(monthly[0].text.strip())
                        scraped_postpaid_price.onetime_price = price_parser(monthly[1].text.strip())
                    if label.find('strong').text == ' Full price':
                        retail = label.findAll('span', class_='display-block')
                        scraped_postpaid_price.retail_price = price_parser(retail[1].text.strip().replace(',', ''))

                # add to database
                remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                          scraped_postpaid_price.storage, scraped_postpaid_price.date)
                add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                         scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                         scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                         scraped_postpaid_price.date, scraped_postpaid_price.time)

                spr_scrape_postpaid_promotions(driver, soup, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                               scraped_postpaid_price.storage)

    driver.quit()



