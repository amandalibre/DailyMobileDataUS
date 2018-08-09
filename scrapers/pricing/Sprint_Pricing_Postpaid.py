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


def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))


def device_parser(string):
    string = str(string)
    string = string.lower()
    string = string.replace("²", "2")
    string = string.replace("³", "3")
    string = string.replace("⁴", "4")
    string = string.replace("⁵", "5")
    string = removeNonAscii(string)
    string = string.replace('motorola moto z force edition 2nd gen', 'moto z2 force edition')
    string = string.replace('motorola moto e 4th gen', 'moto e4')
    string = string.replace(' - exclusively at sprint', '')
    string = string.replace('samsung ', '')
    string = string.replace('apple ', '')
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


# go to website
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() + "\\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.get('https://www.sprint.com/en/shop/cell-phones.html')
time.sleep(5)

# go to Phones url (since url could change)
driver.find_element_by_xpath('/html/body/div[1]/header/div[2]/div/div/div[1]/nav/ul/li[3]/a').click()
time.sleep(1)
driver.find_element_by_link_text('All phones').click()
time.sleep(10)

# get soup
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
driver.close()

# make scraper object
scraped_postpaid_price = ScrapedPostpaidPrice()

# set hardcoded variables
scraped_postpaid_price.provider = 'sprint'
scraped_postpaid_price.date = datetime.date.today()
scraped_postpaid_price.time = datetime.datetime.now().time()

# iterate through devices on landing page
for device_tile in soup.findAll('li', class_='col-xs-24 col-sm-12 col-lg-8 text-center device-tile'):

    # get device name text
    device_name = device_tile.find("h3", {"class": "font-size-18 line-height-24 font-normal my-0"}).text.strip().lower()

    # eliminate out of scope devices
    if device_name.find("linelink") != -1 or device_name.find("pre-owned") != -1 or device_name.find("flip") != -1 \
            or device_name.find("xp5s") != -1 or device_name.find("duraxtp") != -1 or device_name.find("duratr") != -1 \
            or device_name.find("xp strike") != -1 or device_name.find("certified") != -1:
        continue

    # device name
    scraped_postpaid_price.device = device_parser(device_name)

    # url
    scraped_postpaid_price.url = "https://www.sprint.com" + device_tile.find("a")["href"]

    # promo text for device landing page
    try:
        promo_text = device_tile.find("span", {"class": "color--purple font-size-14"}).text.strip()
    except AttributeError:
        promo_text = ''
    add_scraped_promotions_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                       '0', 'device landing page', promo_text,
                                       scraped_postpaid_price.url, scraped_postpaid_price.date,
                                       scraped_postpaid_price.time)

    # go to url
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)
    driver.get(scraped_postpaid_price.url)
    time.sleep(5)
    html = driver.page_source
    device_soup = BeautifulSoup(html, "html.parser")

    # if 404 error, stop program
    site_title = device_soup.find_all("title")
    if '404' in str(site_title):
        print('404 Error: ' + scraped_postpaid_price.device)
        continue

    # check to make sure device name on page is the same as the device_name on the landing page
    device_page_device_name = device_parser(driver.find_element_by_xpath('/html/body/div[1]/article/div[3]/div[1]/div[1]/div[1]/div/div/div[1]/h1').text.strip().lower())
    if device_page_device_name != scraped_postpaid_price.device:
        print('Website Error: ', scraped_postpaid_price.device, ' on landing page, ', device_page_device_name, ' on individual page')
        continue

    # click on drop down menu and record device sizes
    size_selector = driver.find_element_by_id('sprint_storage_selector')
    size_selector.click()
    time.sleep(2)
    sizes = size_selector.text.strip().replace(' GB', '')
    sizes = sizes.split('\n')

    # iterate through sizes
    for size in sizes:

        # click on size and reload page
        select = Select(driver.find_element_by_id('sprint_storage_selector'))
        select.select_by_value(size)
        time.sleep(6)
        html = driver.page_source
        device_soup = BeautifulSoup(html, "html.parser")

        # record device size
        scraped_postpaid_price.storage = size

        # record current url
        scraped_postpaid_price.url = driver.current_url

        # initialize price variables
        scraped_postpaid_price.monthly_price = '0.00'
        scraped_postpaid_price.retail_price = '0.00'
        scraped_postpaid_price.onetime_price = '0.00'

        # get prices
        for label in device_soup.findAll('label', class_='soar-selection__label'):
            if label.find('strong').text == ' Sprint Flex 18-mo. lease':
                monthly = label.findAll('span', class_='display-block')
                scraped_postpaid_price.monthly_price = price_parser(monthly[0].text.strip())
                scraped_postpaid_price.onetime_price = price_parser(monthly[1].text.strip())
            if label.find('strong').text == ' Full price':
                retail = label.findAll('span', class_='display-block')
                scraped_postpaid_price.retail_price = price_parser(retail[1].text.strip().replace(',', ''))

        # if page didn't load all the way
        if scraped_postpaid_price.onetime_price == '0.00' and scraped_postpaid_price.monthly_price == '0.00':

            # close and reload page
            driver.close()
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_driver = os.getcwd() + "\\chromedriver.exe"
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
            driver.get(scraped_postpaid_price.url)
            time.sleep(5)
            html = driver.page_source
            device_soup = BeautifulSoup(html, "html.parser")

            # get prices again
            for label in device_soup.findAll('label', class_='soar-selection__label'):
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
        spr_scrape_postpaid_promotions(device_soup, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                       scraped_postpaid_price.storage)

driver.quit()