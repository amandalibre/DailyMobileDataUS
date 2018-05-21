# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
import datetime

date = datetime.date.today()
time_now = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

def get_link(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    string = "https://www.cricketwireless.com" + string
    return string

def price_parser(string):
    string = string.strip()
    string = string.replace("$", "")
    string = string.replace("*", "")
    return string

def get_cri_device_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    time.sleep(5)
    driver.get("https://www.cricketwireless.com/cell-phones/smartphones")
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    cricket_dict = {}
    count = 0
    for div in soup.findAll('div', class_='row picAndPriceWrapper'):
        for span in div.findAll('span', class_='extraHeaderText'):
            if span.text == 'Pre-Owned' or span.text == 'Certified Pre-Owned':
                for a in div.findAll("a", class_="headline-link"):
                    cricket_dict[count] = {'device_name': remove_colors(a.text.strip()) + ' ' + span.text, 'link': get_link(a)}
                    count += 1
            else:
                for a in div.findAll("a", class_="headline-link"):
                    cricket_dict[count] = {'device_name': remove_colors(a.text.strip()), 'link': get_link(a)}
                    count += 1

    count1 = 0
    for div in soup.findAll('div', class_='phone-price'):
        if div.findAll('div', class_='price current-price'):
            for z in div.findAll('div', class_='price current-price'):
                cricket_dict[count1].update({'price': price_parser(z.text)})
                cricket_dict[count1].update({'retail_price': price_parser(z.text)})
                count1 += 1
        else:
            for y in div.findAll('div', class_='price was-price'):
                cricket_dict[count1].update({'price': price_parser(y.text)})
                cricket_dict[count1].update({'retail_price': price_parser(y.text)})
                count1 += 1

    if count != count1:
        print('For loop counts are different. Program stopped.')

    for device in range(len(cricket_dict)):
        driver.get(cricket_dict[device]['link'])
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if 'GB' in cricket_dict[device]['device_name']:
            storage = cricket_dict[device]['device_name'].split(' ')[-1]
            if storage.replace('GB', '') == '':
                storage = cricket_dict[device]['device_name'].split(' ')[-2] + " " + storage
            device_name = cricket_dict[device]['device_name'].replace(storage, '')
            storage = storage.replace('GB', '')
            cricket_dict[device].update({'device_name': device_name})
        elif soup.findAll('div', class_='specs3 parbase richtext'):
            storage = soup.findAll('div', class_='specs3 parbase richtext')[0]
            if ',' in storage.text:
                storage = storage.text.split(',')
                if 'ROM' in storage[1]:
                    storage = storage[1]
                elif 'ROM' in storage[0]:
                    storage = storage[0]
                storage = storage.split('GB', 2)[0]
                storage = storage.replace("up to ", "")
                storage = storage.strip()
            elif 'RAM' in storage.text:
                storage = storage.text.split('GB RAM')[1]
                storage = storage.split('GB ROM')[0]
                storage = storage.strip()
            else:
                storage = storage.text.split('GB', 2)[0]
                storage = storage.replace("Up to ", "")
                storage = storage.strip()
        else:
            storage = 'N/A'
        cricket_dict[device].update({'storage': storage})

    driver.close()

    return cricket_dict

cricket_dict = get_cri_device_prices()

for x in range(len(cricket_dict)):
    if 'Certified Pre-Owned' not in cricket_dict[x]['device_name']:
        remove_prepaid_duplicate('cricket', cricket_dict[x]['device_name'], cricket_dict[x]['storage'], date)
        add_prepaid_pricing_to_database('cricket', cricket_dict[x]['device_name'], cricket_dict[x]['storage'], cricket_dict[x]['price'], cricket_dict[x]['retail_price'], cricket_dict[x]['link'], date, time_now)