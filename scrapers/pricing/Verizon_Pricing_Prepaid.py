# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException
import time, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import datetime
from data.database.Add_Prepaid_Pricing_To_Database import add_prepaid_pricing_to_database, remove_colors, remove_prepaid_duplicate
from data.model.Scraped_Prepaid_Price import ScrapedPrepaidPrice
import pyautogui

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


def remove_non_ascii(string): return "".join(filter(lambda x: ord(x) < 128, string))


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
    string = remove_non_ascii(string)
    string = string.strip()
    return string


def ver_scrape_prepaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_extension("Full-Page-Screen-Capture_v3.17.crx")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # update Extension options
    driver.get('chrome-extension://fdpohaocaechififmbbbbbknoalclacl/options.html')
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="settings-container"]/div[2]/div[3]/div/label/input').click()
    time.sleep(3)
    pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')
    driver.find_element_by_xpath('//*[@id="settings-container"]/div[2]/div[1]/div/input').send_keys('US-Daily-Screenshots')
    pyautogui.hotkey('tab')
    time.sleep(1)

    # go to website
    driver.get("https://www.verizonwireless.com/prepaid/smartphones/")
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # use keyboard shortcut to activate Full Page Screen Capture extension
    pyautogui.hotkey('alt', 'shift', 'p')
    time.sleep(20)

    # make object
    scraped_prepaid_price = ScrapedPrepaidPrice()

    # set hardcoded variables
    scraped_prepaid_price.provider = 'verizon'
    scraped_prepaid_price.date = datetime.date.today()
    scraped_prepaid_price.time = datetime.datetime.now().time()

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

    # go to every page of device landing pages (there are usually multiple pages)
    for page_link in page_links:
        driver.get(page_link)
        time.sleep(3)

        # use keyboard shortcut to activate Full Page Screen Capture extension
        pyautogui.hotkey('alt', 'shift', 'p')
        time.sleep(20)

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
        if 'Certified Pre-Owned' not in verizon_dict[x]['device_name']:

            # set device name, url and prices
            scraped_prepaid_price.device = verizon_dict[x]['device_name']
            scraped_prepaid_price.url = verizon_dict[x]['link']
            scraped_prepaid_price.retail_price = verizon_dict[x]['price']
            scraped_prepaid_price.list_price = verizon_dict[x]['price']

            # go to url
            driver.get(scraped_prepaid_price.url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # get device storage
            for a in soup.findAll('a', class_='btn dropdown-toggle'):
                for span in a.findAll('span', class_='filter-option')[0]:
                    if 'GB' in span:
                        scraped_prepaid_price.storage = span.replace('GB', '')

            # add to database
            remove_prepaid_duplicate(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                     scraped_prepaid_price.storage, scraped_prepaid_price.date)
            add_prepaid_pricing_to_database(scraped_prepaid_price.provider, scraped_prepaid_price.device,
                                            scraped_prepaid_price.storage, scraped_prepaid_price.list_price,
                                            scraped_prepaid_price.retail_price, scraped_prepaid_price.url,
                                            scraped_prepaid_price.date, scraped_prepaid_price.time)
    driver.quit()





