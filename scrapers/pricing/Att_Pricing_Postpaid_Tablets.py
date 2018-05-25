# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Postpaid_Pricing_To_Database import add_postpaid_to_database, remove_postpaid_duplicate
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from selenium.common.exceptions import NoSuchElementException

def parser(str):
    str = str.strip()
    str = str.replace("</div", "")
    if "Free" in str:
        str = "Free"
    return str

def monthlyparser(str):
    indexstart = (str.find("$"))
    indexend = (str.find("/mo"))
    monthlyprice = str[indexstart + 1:indexend]
    return monthlyprice

def brandparser(string):
    string = string.replace(", Phone by Google", "")
    string = string.replace("with Sapphire Shield", "")
    string = string.replace("Samsung", "")
    string = string.replace("Apple", "")
    string = string.replace("6s", "6S")
    string = string.replace("7s", "7S")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    if "Galaxy J3 (2017)" in string:
        string = "Galaxy J3 (2017)"
    string = removeNonAscii(string)
    string = string.strip()
    string = string.replace('iPad 9.7-inch (6th Gen.)', 'iPad 9.7 (2018)')
    string = string.replace('iPad Pro (12.9-inch)', 'iPad Pro 12.9')
    string = string.replace('iPad Pro (10.5-inch)', 'iPad Pro 10.5')
    string = string.replace('iPad (5th Gen.)', 'iPad 9.7')
    string = string.replace('Galaxy Tab E', 'Galaxy Tab E 8')
    return string

def remove_dollar_sign(string):
    string = str(string)
    string = string.replace('$', '')
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def att_scrape_postpaid_tablet_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # go to website
    driver.get('https://www.att.com/shop/wireless/devices/tablets.html')
    time.sleep(5)

    # make object
    scraped_postpaid_price = ScrapedPostpaidPrice()

    # set hardcoded variables
    scraped_postpaid_price.date = datetime.date.today()
    scraped_postpaid_price.time = datetime.datetime.now().time()
    scraped_postpaid_price.provider = 'att'

    # check if all devices are shown on page
    devices_shown = driver.find_element_by_class_name('deviceCount').text.split(' ')[-1]
    devices_total = driver.find_element_by_class_name('deviceSize').text
    if devices_shown != devices_total:
        # click 'Show All' button if it exists
        if driver.find_element_by_id("deviceShowAllLink"):
            driver.find_element_by_id("deviceShowAllLink").click()
            print('Show All clicked')

    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # create dictionary of all devices on landing page
    att_postpaid_dict = {}

    count = 0
    for div in soup.findAll("div", class_="list-itemHeader"):
        for a in div.findAll("a", class_="titleURLchng"):
            att_postpaid_dict[count] = {'device_name': (brandparser(parser(a.text))).lower()}
            att_postpaid_dict[count].update({'url': 'https://www.att.com' + a['href']})
            # att_postpaid_dict[count].update({'config_url': "https://www.att.com/shop/wireless/deviceconfigurator.html?prefetched=true&sku=" + a['href'].split('=', 1)[1]})
        count += 1

    if len(att_postpaid_dict) == 1:
        print("Only one device was scraped. Program stopped.")
        driver.quit()
        exit()

    for device in range(len(att_postpaid_dict)):

        # set object's device name
        scraped_postpaid_price.device = att_postpaid_dict[device]['device_name']

        # eliminate pre-owned devices
        if 'certified' not in scraped_postpaid_price.device:

            # if device size in storage, take it out
            if 'gb' in att_postpaid_dict[device]['device_name']:
                device_name_words = att_postpaid_dict[device]['device_name'].split(' ')
                for word in device_name_words:
                    if 'gb' in word:
                        scraped_postpaid_price.device = scraped_postpaid_price.device.replace(' - ' + word, '')

            # go to url and get storage size
            driver.get(att_postpaid_dict[device]['url'])
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # read size from size button that is in html even if it is not visible on page
            # iterate through each size
            button_number = 0
            for button in soup.findAll('button', class_='preSize'):

                # go back to base web page if there is more than one button
                if button_number > 0:
                    driver.get(att_postpaid_dict[device]['url'])
                    time.sleep(3)

                device_storage = button.text.replace('GB', '').strip()
                if 'MB' in device_storage:
                    device_storage = device_storage.replace('MB', '')
                    device_storage = '{: .2f}'.format(int(device_storage) * 0.001)

                # set object's storage size
                scraped_postpaid_price.storage = device_storage
                size_id = 'size_' + scraped_postpaid_price.storage + 'GB'
                size = driver.find_element_by_id(size_id)

                # if popup is there, click it and make it go away
                try:
                    driver.find_element_by_xpath('//*[@id="acsMainInvite"]/a').click()
                    print('popup clicked')
                except NoSuchElementException:
                    print('no popup')

                # click on size that was recorded as storage if there is more than one storage size
                if len(soup.findAll('button', class_='preSize')) != 1:
                    size.click()
                    time.sleep(2)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                # get sku for correct url and config_url
                try:
                    sku = soup.find(id='skuIDToDisplay').text.strip()
                except AttributeError:
                    sku = 'sku' + soup.find('att-product-viewer')['skuid']

                # set url and config_url for object
                url = att_postpaid_dict[device]['url'].split('=sku')[0] + '=sku' + sku
                config_url = 'https://www.att.com/shop/wireless/deviceconfigurator.html?prefetched=true&sku=' + sku
                scraped_postpaid_price.config_url = config_url
                scraped_postpaid_price.url = url

                # if there is no device_storage entry (due to differently formatted pages)
                if scraped_postpaid_price.storage == 'N/A':
                    print('storage size in specs')
                    for div in soup.findAll('div', class_='technicalspecification parbase technicalspecificati additionaldetail'):
                        if div.find('div', class_='fltL').text == 'Internal memory storage':
                            device_storage = div.find('div', class_='fltLIco').text.strip().replace('GB', '')
                            att_postpaid_dict[device].update({'device_storage': device_storage})

                # go to config_url and get prices
                driver.get(scraped_postpaid_price.config_url)
                time.sleep(3)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                if len(soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5')) > 1:
                    for div in soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5'):
                        for span in div.findAll('span', class_='text-xlarge margin-right-5 adjustLetterSpace ng-binding ng-scope'):
                            if span.text == 'AT&T Next Every Year℠':
                                contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.monthly_price = remove_dollar_sign(contract_prices[0].text)
                                scraped_postpaid_price.monthly_price = remove_dollar_sign(contract_prices[1].text)
                            if span.text == 'No annual contract':
                                no_contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.retail_price = remove_dollar_sign(no_contract_prices[0].text.replace(',', ''))
                            if span.text == '2-Year Contract':
                                no_contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.contract_ufc = remove_dollar_sign(no_contract_prices[0].text)
                else:
                    for div in soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5'):
                        for span in div.findAll('span', class_='text-xlarge margin-right-5 adjustLetterSpace ng-binding ng-scope'):
                            if span.text == 'No annual contract':
                                no_contract_prices = div.findAll('div', class_='attOrange text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.retail_price = remove_dollar_sign(no_contract_prices[0].text)

                # print device info
                print(scraped_postpaid_price.device, scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                      scraped_postpaid_price.retail_price, scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                      scraped_postpaid_price.config_url)

                # add to database
                remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                          scraped_postpaid_price.storage, scraped_postpaid_price.date)
                add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
                                         scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
                                         scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
                                         scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
                                         scraped_postpaid_price.date, scraped_postpaid_price.time)
                button_number += 1

    driver.quit()


att_scrape_postpaid_tablet_prices()

