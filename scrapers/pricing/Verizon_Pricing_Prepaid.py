# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException
import time, re
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

def is_element_present(self, how, what):
    try: self.driver.find_element(by=how, value=what)
    except NoSuchElementException as e: return False
    return True

def parser(string):
    indexstart = (string.find("$"))
    indexend = (string.find("/mo"))
    string = string[indexstart+1:indexend]
    string = string.strip()
    string = string.replace("\n", "")
    string = string.replace("Starts at", "")
    string = string.strip()
    string = re.sub("[^0-9]", "", string)
    string = str(float(string)/100)
    return string

def parser2(string):
    string = string.replace("\n", "")
    string = string.replace("Starts at", "")
    string = string.strip()
    if "was" in string:
        indexstart = (string.find("was"))
        string = string[indexstart+11:indexstart+17]
    else:
        indexstart = (string.find("$"))
        string = string[indexstart+1:indexstart+7]
        string = string.strip()
    return string

def link_parser(string):
    string = string.split('data-pdpurl="', 1)[1]
    string = string.split('"', 1)[0]
    return string

def page_link_parser(string):
    string = str(string)
    string = string.split('href="', 1)[1]
    string = string.split('"', 1)[0]
    return string

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
    string = string.replace("LG", "LG ")
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
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def get_ver_device_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)
    time.sleep(5)
    driver.get("https://www.verizonwireless.com/prepaid/smartphones/")
    time.sleep(3)

    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # get links for all the device pages
    page_links = []
    for a in soup.findAll('a', class_='page-link')[:-1]:
        page_links.append('https://www.verizonwireless.com/prepaid/smartphones/' + page_link_parser(a))

    verizon_dict = {}
    dict_count = 0

    for div in soup.findAll('div', class_='gridwallTile c-gridwallTile prepaidGridwallTile'):
        verizon_dict[dict_count] = {'link': 'https://www.verizonwireless.com' + link_parser(str(div))}
        for h6 in div.findAll("h6", class_="gridwallTile_deviceName"):
            verizon_dict[dict_count].update({'device_name': remove_colors(brandparser(h6.text))})
        for div in div.findAll("div", class_="fontSize_6"):
            price = parser2(div.text)
            if '$' in price:
                price = price.replace('$', '')
            verizon_dict[dict_count].update({'price': price})
        dict_count += 1

    for page_link in page_links:
        driver.get(page_link)
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        for div in soup.findAll('div', class_='gridwallTile c-gridwallTile prepaidGridwallTile'):
            verizon_dict[dict_count] = {'link': 'https://www.verizonwireless.com' + link_parser(str(div))}
            for h6 in div.findAll("h6", class_="gridwallTile_deviceName"):
                verizon_dict[dict_count].update({'device_name': remove_colors(brandparser(h6.text))})
            for div in div.findAll("div", class_="fontSize_6"):
                price = parser2(div.text)
                if '$' in price:
                    price = price.replace('$', '')
                verizon_dict[dict_count].update({'price': price})
            dict_count += 1

    for x in range(len(verizon_dict)):
        driver.get(verizon_dict[x]['link'])
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.findAll('a', class_='btn dropdown-toggle'):
            for span in a.findAll('span', class_='filter-option')[0]:
                if 'GB' in span:
                    storage = span.replace('GB', '')
                    verizon_dict[x].update({'storage': storage})
        if 'storage' not in verizon_dict[x]:
            verizon_dict[x].update({'storage': 'NA'})

    driver.quit()
    return verizon_dict

verizon_dict = get_ver_device_prices()

for x in range(len(verizon_dict)):
    if 'Certified Pre-Owned' not in verizon_dict[x]['device_name']:
        remove_prepaid_duplicate('verizon', verizon_dict[x]['device_name'], verizon_dict[x]['storage'], date)
        add_prepaid_pricing_to_database('verizon', verizon_dict[x]['device_name'], verizon_dict[x]['storage'], verizon_dict[x]['price'],
                                        verizon_dict[x]['price'], verizon_dict[x]['link'], date, time_now)