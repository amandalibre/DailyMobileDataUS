# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from data.database.Add_Postpaid_Pricing_To_Database import remove_postpaid_duplicate, add_postpaid_to_database
from selenium.common.exceptions import NoSuchElementException

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

date = datetime.date.today()
time_now = datetime.datetime.now().time()

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
    string = string.lower()
    return string

def remove_dollar_sign(string):
    string = str(string)
    string = string.replace('$', '')
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

def get_att_postpaid_prices():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(6)
    driver.get('https://www.att.com/shop/wireless/devices/smartphones.html')
    time.sleep(2)

    # check if all devices are shown on page
    devices_shown = driver.find_element_by_class_name('deviceCount').text.split(' ')[-1]
    devices_total = driver.find_element_by_class_name('deviceSize').text
    if devices_shown != devices_total:
        # click 'Show All' button if it exists
        if driver.find_element_by_id("deviceShowAllLink"):
            driver.find_element_by_id("deviceShowAllLink").click()
            print('Show All clicked')

    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    att_postpaid_dict = {}

    count = 0
    for div in soup.findAll("div", class_="list-item xref"):
        for a in div.findAll("a", class_=" titleURLchng"):
            att_postpaid_dict[count] = {'device_name': (brandparser(parser(a.text)).lower())}
        for a in div.findAll("a", class_="clickStreamSingleItem imageURLchng"):
            att_postpaid_dict[count].update({'url': 'https://www.att.com' + a['href']})
            att_postpaid_dict[count].update({'config_url': "https://www.att.com/shop/wireless/deviceconfigurator.html?prefetched=true&sku=" + a['href'].split('=', 1)[1]})
        count += 1

    if len(att_postpaid_dict) == 1:
        print("Only one device was scraped. Program stopped.")
        driver.quit()
        exit()

    for device in range(len(att_postpaid_dict)):
        # go to url and get storage size
        driver.get(att_postpaid_dict[device]['url'])
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # read size from size button that is in html even if it is not visible on page
        # if there is more than one storage size, click on the smallest one
        if len(soup.findAll('button', class_='preSize')) > 1:
            for button in soup.findAll('button', class_='preSize'):
                att_postpaid_dict[device].update({'device_storage': button.text.replace('GB', '').strip()})
                smallest_size_id = 'size_' + att_postpaid_dict[device]['device_storage'] + 'GB'
                smallest_size = driver.find_element_by_id(smallest_size_id)
                # if popup is there, click it and make it go away
                try:
                    driver.find_element_by_xpath('//*[@id="acsMainInvite"]/a').click()
                    print('popup clicked')
                except NoSuchElementException:
                    print('no popup')
                smallest_size.click()
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                updated_sku = soup.find(id='skuIDToDisplay').text.strip()
                updated_config_url = 'https://www.att.com/shop/wireless/deviceconfigurator.html?prefetched=true&sku=' + updated_sku
                att_postpaid_dict[device].update({'config_url': updated_config_url})
                break
        # if there is only one storage size, we record that number
        else:
            for button in soup.findAll('button', class_='preSize'):
                device_storage = button.text.replace('GB', '').strip()
                if 'MB' in device_storage:
                    device_storage = device_storage.replace('MB', '')
                    device_storage = '{: .2f}'.format(int(device_storage) * 0.001)
                att_postpaid_dict[device].update({'device_storage': device_storage})

        # go to config_url and get prices
        driver.get(att_postpaid_dict[device]['config_url'])
        time.sleep(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if len(soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5')) > 1:
            for div in soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5'):
                for span in div.findAll('span', class_='text-xlarge margin-right-5 adjustLetterSpace ng-binding ng-scope'):
                    if span.text == 'AT&T Next Every Year℠':
                        contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                        att_postpaid_dict[device].update({'onetime_price': remove_dollar_sign(contract_prices[0].text)})
                        att_postpaid_dict[device].update({'monthly_price': remove_dollar_sign(contract_prices[1].text)})
                    if span.text == 'No annual contract':
                        no_contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                        att_postpaid_dict[device].update({'retail_price': remove_dollar_sign(no_contract_prices[0].text)})
        else:
            for div in soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5'):
                for span in div.findAll('span', class_='text-xlarge margin-right-5 adjustLetterSpace ng-binding ng-scope'):
                    if span.text == 'No annual contract':
                        no_contract_prices = div.findAll('div', class_='attOrange text-cramped text-xlarge text-nowrap pad-bottom-10')
                        att_postpaid_dict[device].update({'retail_price': remove_dollar_sign(no_contract_prices[0].text)})
                        att_postpaid_dict[device].update({'onetime_price': '0.00'})
                        att_postpaid_dict[device].update({'monthly_price': '0.00'})

        print(att_postpaid_dict[device])

    driver.quit()

    # add prices to database
    for device in range(len(att_postpaid_dict)):
        if 'certified pre-owned' not in att_postpaid_dict[device]['device_name'] and \
              'flip' not in att_postpaid_dict[device]['device_name'] and \
                'wireless' not in att_postpaid_dict[device]['device_name'] and \
                'lg b470' not in att_postpaid_dict[device]['device_name'] and \
                'xp5s' not in att_postpaid_dict[device]['device_name']:
            remove_postpaid_duplicate('att', att_postpaid_dict[device]['device_name'],
                                      att_postpaid_dict[device]['device_storage'], date)
            add_postpaid_to_database('att', att_postpaid_dict[device]['device_name'],
                                     att_postpaid_dict[device]['device_storage'],
                                    att_postpaid_dict[device]['monthly_price'], att_postpaid_dict[device]['onetime_price'],
                                    att_postpaid_dict[device]['retail_price'], '0.00',
                                    att_postpaid_dict[device]['url'], date, time_now)


get_att_postpaid_prices()

