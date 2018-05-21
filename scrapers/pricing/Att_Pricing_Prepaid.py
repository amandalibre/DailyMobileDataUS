# -*- coding: utf-8 -*-
import datetime
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, \
    remove_prepaid_duplicate


date = datetime.date.today()
time_now = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

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

def get_att_device_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    time.sleep(5)
    driver.get("https://www.att.com/shop/wireless/devices/prepaidphones.html")
    time.sleep(10)
    driver.find_element_by_id(id_='showAllDevicesText').click()
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

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
        driver.get(att_dict[device]['link'])
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if soup.find(id='putMemoryHere'):
            span = soup.find(id='putMemoryHere')
            storage = span.text.replace('GB', '')
            att_dict[device].update({'storage': storage})
        elif soup.findAll('div', class_='tiny-accordion ng-isolate-scope'):
            memory = soup.findAll('div', class_='tiny-accordion ng-isolate-scope')[0]
            for div in memory.findAll('div', class_='span9 description')[15]:
                storage = div.strip()
                storage = storage.replace('Up to ', '')
                att_dict[device].update({'storage': storage})
        else:
            for next in soup.findAll('div', class_='fltLIco'):
                if 'GB' in next.text:
                    storage = next.text.strip()
                    storage = storage.split(' ')[-1].replace('GB', '')
                    att_dict[device].update({'storage': storage})
                    break
        if 'storage' not in att_dict[device]:
            att_dict[device].update({'storage': 'N/A'})
        if 'GB' in att_dict[device]['storage']:
            att_dict[device].update({'storage': att_dict[device]['storage'].replace('GB', '')})

    driver.close()

    return att_dict

att_dict = get_att_device_prices()

for x in range(len(att_dict)):
    if 'AT&T Certified Restored' not in att_dict[x]['device_name'] and 'LG B470' not in att_dict[x]['device_name']:
        remove_prepaid_duplicate('att', att_dict[x]['device_name'], att_dict[x]['storage'], date)
        add_prepaid_pricing_to_database('att', att_dict[x]['device_name'], att_dict[x]['storage'], att_dict[x]['price'], att_dict[x]['retail_price'], att_dict[x]['link'], date, time_now)
