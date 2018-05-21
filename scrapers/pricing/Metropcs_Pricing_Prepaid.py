# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate

date = datetime.date.today()
time_now = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

def price_parser(string):
    string = string.replace("00", ".00")
    string = string.replace("$", "")
    return string

def link_parser(string):
    string = str(string)
    string = string.split('pdl_track_phone_title_click="', 1)[1]
    string = string.split('"', 1)[0]
    string = string.replace('| ', '/')
    string = string.replace(' ', '-')
    string = 'https://www.metropcs.com/shop/phones/details/' + string
    return string

def get_met_device_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    time.sleep(5)
    driver.get("https://www.metropcs.com/shop/phones")
    time.sleep(15)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    metropcs_dict = {}
    count = 0
    for span in soup.findAll("span", class_="cursor"):
        metropcs_dict[count] = {'device_name': remove_colors(span.text).strip(), 'link': link_parser(span)}
        count += 1

    count1 = 0
    for div in soup.findAll("div", class_="card-content card-price"):
        if "After all offers" in div.text:
            for span in div("span", class_="current-price"):
                metropcs_dict[count1].update({'price': price_parser(span.text.replace('\n', ''))})
            for span in div("span", class_="normal-price"):
                metropcs_dict[count1].update({'retail_price': price_parser(span.text.replace('\n', ''))})
            count1 += 1
        else:
            for span in div("span", class_="current-price"):
                metropcs_dict[count1].update({'price': price_parser(span.text.replace('\n', ''))})
                metropcs_dict[count1].update({'retail_price': price_parser(span.text.replace('\n', ''))})
            count1 += 1

    if count != count1:
        print('For loop counts are different. Program stopped.')

    for device in range(len(metropcs_dict)):
        if 'Hotspot' not in metropcs_dict[device]['device_name'] and 'SIM' not in metropcs_dict[device]['device_name']:
            driver.get(metropcs_dict[device]['link'])
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            # one hardcoded exception
            if metropcs_dict[device]['device_name'] == 'HTC Desire 530':
                storage = '16'
                metropcs_dict[device].update({'storage': storage})
            # for devices with the storage size in the device_name
            elif metropcs_dict[device]['device_name'].find('GB') != -1:
                storage = metropcs_dict[device]['device_name'].split(' ')[-1]
                device_name = metropcs_dict[device]['device_name'].replace(storage, '')
                metropcs_dict[device].update({'device_name': device_name.strip()})
                storage = storage.replace('GB', '')
                metropcs_dict[device].update({'storage': storage})
            # for devices with specs preview wrapper under header
            elif 'storage' not in metropcs_dict[device]:
                for p in soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        storage = p.text.split(' ')[0].replace('GB', '')
                        metropcs_dict[device].update({'storage': storage})
                        break
                if 'storage' not in metropcs_dict[device]:
                    for span in soup.findAll('span', class_='p-l-5 v-align-super'):
                        if 'GB' in span.text:
                            storage = span.text.split(' ')[0].replace('GB', '')
                            metropcs_dict[device].update({'storage': storage})
                            break
            elif 'storage' not in metropcs_dict[device]:
                for p in soup.findAll('p', class_='m-b-0 text-bold'):
                    if 'GB' in p.text:
                        storage = p.text.split(' ')[0].replace('GB', '')
                        metropcs_dict[device].update({'storage': storage})
                        break
            if 'storage' not in metropcs_dict[device]:
                metropcs_dict[device].update({'storage': 'ERROR'})

    driver.close()

    return metropcs_dict

metropcs_dict = get_met_device_prices()

for x in range(len(metropcs_dict)):
    if 'Hotspot' not in metropcs_dict[x]['device_name'] and 'SIM' not in metropcs_dict[x]['device_name']:
        remove_prepaid_duplicate('metropcs', metropcs_dict[x]['device_name'], metropcs_dict[x]['storage'], date)
        add_prepaid_pricing_to_database('metropcs', metropcs_dict[x]['device_name'], metropcs_dict[x]['storage'], metropcs_dict[x]['price'], metropcs_dict[x]['retail_price'], metropcs_dict[x]['link'], date, time_now)
