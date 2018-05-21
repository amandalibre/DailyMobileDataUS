# -*- coding: utf-8 -*-
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate

date = datetime.date.today()
time_now = datetime.datetime.now().time()

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def brandparser(string):
    string = string.replace("\n", "")
    string = string.replace("Google", "")
    string = string.replace("Samsung", "")
    string = string.replace("MOTO", "Moto")
    string = string.replace("LG", "LG ")
    string = string.replace("ZTE", "ZTE ")
    string = string.replace("HTC", "HTC ")
    string = string.replace("Optimus ", "")
    string = string.replace("Apple", "")
    string = string.replace('ASUS', 'ASUS ')
    string = string.replace("Prepaid", "")
    string = string.replace(", Phone by", "")
    string = string.replace("with Sapphire Shield", "")
    string = string.replace("Google", "")
    string = string.replace("Samsung", "")
    string = string.replace("HTC", "HTC ")
    # string = string.replace("LG", "LG ")
    string = string.replace("Motorola", "")
    string = string.replace('Kyocera', 'Kyocera ')
    string = string.replace("Apple", "")
    string = string.replace("E4", "e4")
    string = string.replace("  ", " ")
    string = string.replace(" Black", "")
    string = string.replace(" Space Gray", "")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    string = removeNonAscii(string)
    string = string.strip()
    string = string.lower()
    return string

def link_parser(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    return string

def monthly_price_parser(string):
    string = str(string)
    string = string.split('/mo.')[0]
    string = string.replace('$', '')
    return string

def retail_price_parser(string):
    string = str(string)
    string = string.replace('Retail Price', '')
    string = string.replace('$', '')
    return string

def get_ver_postpaid_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.get("https://www.verizonwireless.com/smartphones/")
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    ver_postpaid_dict = {}

    coming_soon = []
    count = 0
    for div in soup.findAll('div', class_='cursorPointer pad15 onlySidePad tile background_supporting border_CC'):
        for a in div.findAll('a'):
            ver_postpaid_dict[count] = {'device_name': brandparser(a.text)}
            ver_postpaid_dict[count].update({'url': 'https://www.verizonwireless.com' + link_parser(a)})
            break
        for div2 in div.findAll('div', class_='NHaasTX55Rg'):
            if div2.text == 'Not available with the current pricing.':
                coming_soon.append(ver_postpaid_dict[count]['device_name'])
        count += 1

    for device in range(len(ver_postpaid_dict)):
        if 'certified pre-owned' not in ver_postpaid_dict[device]['device_name'] and \
                ver_postpaid_dict[device]['device_name'] not in coming_soon:
            driver.get(ver_postpaid_dict[device]['url'])
            time.sleep(5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            values_list = soup.findAll('div', class_='sizePad')
            ver_postpaid_dict[device].update({'device_storage': values_list[0].text.replace('GB', '')})
            ver_postpaid_dict[device].update({'monthly_price': monthly_price_parser(values_list[-2].text)})
            ver_postpaid_dict[device].update({'retail_price': retail_price_parser(values_list[-1].text)})
            print(ver_postpaid_dict[device])

    driver.close()

    for device in range(len(ver_postpaid_dict)):
        if 'certified pre-owned' not in ver_postpaid_dict[device]['device_name'] and \
                ver_postpaid_dict[device]['device_name'] not in coming_soon:
            remove_postpaid_duplicate('verizon', ver_postpaid_dict[device]['device_name'],
                                      ver_postpaid_dict[device]['device_storage'], date)
            add_postpaid_to_database('verizon', ver_postpaid_dict[device]['device_name'],
                                     ver_postpaid_dict[device]['device_storage'],
                                     ver_postpaid_dict[device]['monthly_price'], '0.00',
                                     ver_postpaid_dict[device]['retail_price'],
                                     '0.00', ver_postpaid_dict[device]['url'], date, time_now)

get_ver_postpaid_prices()

