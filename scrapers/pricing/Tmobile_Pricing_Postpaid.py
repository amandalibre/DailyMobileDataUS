# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate

date = datetime.date.today()
time_now = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def device_parser(string):
    string = str(string)
    string = removeNonAscii(string)
    string = string.replace('plus', 'Plus')
    string = string.replace('Motorola Moto Z Force Edition 2nd Gen', 'Moto Z2 Force Edition')
    string = string.replace('Motorola Moto E 4th Gen', 'Moto e4')
    string = string.replace('Apple ', '')
    string = string.replace('Samsung ', '')
    string = string.lower()
    string = string.replace('galaxy s9 plus', 'galaxy s9+')
    string = string.replace('t-mobile', 'tmobile')
    return string

def monthly_price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    string = string.split('/mo')[0]
    return string

def get_tmobile_postpaid_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)
    driver.get('https://www.t-mobile.com/')
    time.sleep(5)

    # go to Phones url (since url could change)
    phones = driver.find_element_by_xpath('/ html / body / header / nav / div[2] / div[1] / ul / li[2] / a')
    print(phones.text)
    driver.find_element_by_link_text('PHONES').click()
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    tmo_postpaid_dict = {}

    count = 0
    for div in soup.findAll('div', class_='tile col-lg-3 col-md-4 col-sm-6 col-xs-12'):
        a = div.find('a', class_='m-b-5 product-name text-center regular block ng-binding')
        tmo_postpaid_dict[count] = {'device_name': device_parser(a.text)}
        tmo_postpaid_dict[count].update({'url': 'https://www.t-mobile.com/' + a['href']})
        count += 1

    for device in range(len(tmo_postpaid_dict)):
        # go to individual device page
        if 'certified pre-owned' not in tmo_postpaid_dict[device]['device_name'] and \
              'linelink' not in tmo_postpaid_dict[device]['device_name'] and \
              'sim' not in tmo_postpaid_dict[device]['device_name'] and \
              'flip' not in tmo_postpaid_dict[device]['device_name']:
            driver.get(tmo_postpaid_dict[device]['url'])
            time.sleep(6)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            # click on smallest storage size and record it
            for a in soup.findAll('a', class_='memory-btn'):
                tmo_postpaid_dict[device].update({'device_storage': a.text.replace('GB', '').strip()})
                break
            if len(soup.findAll('div', class_='price-lockup')) > 1:
                downpayment_and_retail = soup.findAll('span', class_='cost-price font-tele-ult ng-binding')
                tmo_postpaid_dict[device].update({'onetime_price': downpayment_and_retail[0].text})
                tmo_postpaid_dict[device].update({'retail_price': downpayment_and_retail[1].text})
                monthly_price = soup.find('p', class_='small font-tele-nor m-t-10 ng-binding').text
                tmo_postpaid_dict[device].update({'monthly_price': monthly_price_parser(monthly_price)})
            else:
                onetime_price = soup.find('span', class_='cost-price font-tele-ult ng-binding').text
                tmo_postpaid_dict[device].update({'onetime_price': onetime_price})
                tmo_postpaid_dict[device].update({'retail_price': '0.00'})
                tmo_postpaid_dict[device].update({'monthly_price': '0.00'})
            print(tmo_postpaid_dict[device])

    driver.quit()

    # add prices to database
    for device in range(len(tmo_postpaid_dict)):
        if 'certified pre-owned' not in tmo_postpaid_dict[device]['device_name'] and \
              'linelink' not in tmo_postpaid_dict[device]['device_name'] and \
              'sim' not in tmo_postpaid_dict[device]['device_name'] and \
              'flip' not in tmo_postpaid_dict[device]['device_name']:
            remove_postpaid_duplicate('tmobile', tmo_postpaid_dict[device]['device_name'],
                                      tmo_postpaid_dict[device]['device_storage'], date)
            add_postpaid_to_database('tmobile', tmo_postpaid_dict[device]['device_name'],
                                      tmo_postpaid_dict[device]['device_storage'],
                                      tmo_postpaid_dict[device]['monthly_price'],
                                      tmo_postpaid_dict[device]['onetime_price'],
                                      tmo_postpaid_dict[device]['retail_price'], '0.00',
                                      tmo_postpaid_dict[device]['url'], date, time_now)


get_tmobile_postpaid_prices()

