# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from scrapers.promotions.Tmobile_Promotions_Postpaid import tmo_scrape_postpaid_promotions


def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))


def device_parser(string):
    string = str(string)
    string = removeNonAscii(string)
    string = string.replace('plus', 'Plus')
    string = string.replace('Motorola Moto Z Force Edition 2nd Gen', 'Moto Z2 Force Edition')
    string = string.replace('Motorola Moto E 4th Gen', 'Moto e4')
    string = string.replace('Motorola', '')
    string = string.replace('Apple ', '')
    string = string.replace('Samsung ', '')
    string = string.lower()
    string = string.replace('galaxy s9 plus', 'galaxy s9+')
    string = string.replace('t-mobile', 'tmobile')
    string = string.replace('e play 5th gen', 'e5 play')
    string = string.replace('e plus 5th gen', 'e5 plus')
    string = string.replace('moraccan blue', '')
    string = string.replace('-', '')
    string = string.replace('q7+', 'q7 plus')
    string = string.strip()
    return string


def monthly_price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    string = string.split('/mo')[0]
    return string


def tmo_scrape_postpaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.t-mobile.com/')
    time.sleep(5)

    # go to Phones url from homepage (since url could change)
    driver.find_element_by_link_text('PHONES').click()
    time.sleep(20)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make object
    scraped_postpaid_price = ScrapedPostpaidPrice()

    # hardcoded variables
    scraped_postpaid_price.provider = 'tmobile'
    scraped_postpaid_price.date = datetime.date.today()
    scraped_postpaid_price.time = datetime.datetime.now().time()

    errors = []

    # get device name and url from device landing page
    for tariff in soup.findAll('div', class_='tile col-lg-3 col-md-4 col-sm-6 col-xs-12'):

        device_contents = tariff.find('a', class_='m-b-5 product-name text-center regular block ng-binding')
        scraped_postpaid_price.device = device_parser(device_contents.text)

        if scraped_postpaid_price.device.find('certified pre-owned') == -1 and \
                scraped_postpaid_price.device.find('linelink') == -1 and \
                scraped_postpaid_price.device.find('sim') == -1 and \
                scraped_postpaid_price.device.find('flip') == -1:

            scraped_postpaid_price.url = 'https://www.t-mobile.com/' + device_contents['href']

            promo_text = tariff.find('div', class_='offerTextHeight').text
            if promo_text != '':
                add_scraped_promotions_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                                   '0', 'device landing page', promo_text,
                                                   scraped_postpaid_price.url, scraped_postpaid_price.date,
                                                   scraped_postpaid_price.time)

            # go to individual page
            driver.get(scraped_postpaid_price.url)
            time.sleep(6)
            html = driver.page_source
            device_soup = BeautifulSoup(html, "html.parser")

            # try/except in case of no price (coming soon, etc.)
            try:

                # iterate through storage sizes
                for memory_button in device_soup.findAll('a', class_='memory-btn'):

                    # record storage size and url
                    scraped_postpaid_price.storage = memory_button.text.replace('GB', '').strip()
                    scraped_postpaid_price.url = scraped_postpaid_price.url.split('?memory=')[0] + '?memory=' + scraped_postpaid_price.storage + 'gb'
                    driver.get(scraped_postpaid_price.url)
                    time.sleep(5)
                    html = driver.page_source
                    device_soup = BeautifulSoup(html, "html.parser")

                    if len(device_soup.findAll('div', class_='price-lockup')) > 1:
                        downpayment_and_retail = device_soup.findAll('span', class_='cost-price font-tele-ult ng-binding')
                        scraped_postpaid_price.onetime_price = downpayment_and_retail[0].text
                        scraped_postpaid_price.retail_price = downpayment_and_retail[1].text.replace(',', '')
                        scraped_postpaid_price.monthly_price = monthly_price_parser(device_soup.find('p', class_='small font-tele-nor m-t-10 ng-binding').text)
                    else:
                        scraped_postpaid_price.onetime_price = device_soup.find('span', class_='cost-price font-tele-ult ng-binding').text

                    # add to database
                    remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                              scraped_postpaid_price.storage, scraped_postpaid_price.date)
                    add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                             scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                             scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                             scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                             scraped_postpaid_price.date, scraped_postpaid_price.time)

                    tmo_scrape_postpaid_promotions(driver, soup, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                                   scraped_postpaid_price.storage)

            except AttributeError:
                errors.append(scraped_postpaid_price.device)
                pass

    print("pricing errors: ", errors)
    driver.quit()



