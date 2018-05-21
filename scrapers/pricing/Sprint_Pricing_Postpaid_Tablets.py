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
    string = string.replace(' - Exclusively at Sprint', '')
    string = string.replace('Samsung ', '')
    string = string.replace('Apple ', '')
    string = string.replace('10.5-inch iPad Pro', 'iPad Pro 10.5')
    string = string.replace('12.9-inch iPad Pro', 'iPad Pro 12.9')
    string = string.replace('iPad (6th generation)', 'iPad 9.7 (2018)')
    string = string.replace(' (Latest Model)', '')
    string = string.replace('Galaxy Tab E', 'Galaxy Tab E 8')
    string = string.lower()
    return string

def price_parser(string):
    string = str(string)
    string = string.replace('$', '')
    string = string.split('/')[0]
    if '\n' in string:
        string = string.split('\n')[1]
    return string

def get_sprint_postpaid_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)
    driver.get('https://www.sprint.com/en/shop/tablets.html')
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

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
        driver.get(spr_postpaid_dict[device]['url'])
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        site_title = soup.find_all("title")
        if '404' in site_title:
            print('404 Error: ' + spr_postpaid_dict[device]['device_name'])
            break
        else:
            # click on lowest device size and record it as device_storage
            selector = driver.find_element_by_id('sprint_storage_selector')
            selector.click()
            option_1 = driver.find_element_by_xpath('// *[ @ id = "sprint_storage_selector"] / option[1]')
            option_1.click()
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            spr_postpaid_dict[device].update({'device_storage': option_1.text.replace(' GB', '')})
            # get prices
            for label in soup.findAll('label', class_='soar-selection__label'):
                if label.find('strong').text == ' Buy it with 24 monthly installments':
                    monthly = label.findAll('span', class_='display-block')
                    spr_postpaid_dict[device].update({'monthly_price': price_parser(monthly[0].text.strip())})
                    spr_postpaid_dict[device].update({'onetime_price': price_parser(monthly[1].text.strip())})
                if label.find('strong').text == ' Full price':
                    retail = label.findAll('span', class_='display-block')
                    spr_postpaid_dict[device].update({'retail_price': price_parser(retail[1].text.strip())})

        print(spr_postpaid_dict[device])

    driver.quit()

    # add prices to database
    for device in range(len(spr_postpaid_dict)):
        if 'pre-owned' not in spr_postpaid_dict[device]['device_name'] and \
              'linelink' not in spr_postpaid_dict[device]['device_name'] and \
              'sim' not in spr_postpaid_dict[device]['device_name'] and \
              'flip' not in spr_postpaid_dict[device]['device_name']:
            remove_postpaid_duplicate('sprint', spr_postpaid_dict[device]['device_name'],
                                      spr_postpaid_dict[device]['device_storage'], date)
            add_postpaid_to_database('sprint', spr_postpaid_dict[device]['device_name'],
                                      spr_postpaid_dict[device]['device_storage'],
                                      spr_postpaid_dict[device]['monthly_price'],
                                      spr_postpaid_dict[device]['onetime_price'],
                                      spr_postpaid_dict[device]['retail_price'], '0.00',
                                      spr_postpaid_dict[device]['url'], date, time_now)


get_sprint_postpaid_prices()

