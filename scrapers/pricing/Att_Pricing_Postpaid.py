# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import os
from data.database.Add_Postpaid_Pricing_To_Database import remove_postpaid_duplicate, add_postpaid_to_database
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice
from scrapers.promotions.Att_Promotions_Postpaid import att_scrape_postpaid_promotions

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

def att_scrape_postpaid_smartphone_prices():
    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(6)

    # go to website
    driver.get('https://www.att.com/shop/wireless/devices/cellphones.html')
    time.sleep(2)

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
        driver.find_element_by_id("deviceShowAllLink").click()

    # wait, then open thing
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # create dictionary of all devices on landing page
    att_postpaid_dict = {}

    # parse through device tiles
    count = 0
    for div in soup.findAll("div", class_="list-item"):
        for a in div.findAll("a", class_="titleURLchng"):
            att_postpaid_dict[count] = {'device_name': (brandparser(parser(a.text))).lower()}
            att_postpaid_dict[count].update({'url': 'https://www.att.com' + a['href']})
        deal_landing_page_promo = div.findAll("div", class_="holidayFlag")
        if len(deal_landing_page_promo) == 2 and 'certified' not in att_postpaid_dict[count]['device_name'] and 'flip' \
                not in att_postpaid_dict[count]['device_name'] and 'wireless' not in att_postpaid_dict[count]['device_name']\
                and 'lg b470' not in att_postpaid_dict[count]['device_name'] and 'xp5s' not in att_postpaid_dict[count]['device_name']:
            add_scraped_promotions_to_database(scraped_postpaid_price.provider, att_postpaid_dict[count]['device_name'],
                                               '0', 'device landing page', deal_landing_page_promo[1].img['title'],
                                               att_postpaid_dict[count]['url'], scraped_postpaid_price.date,
                                               scraped_postpaid_price.time)
        count += 1

    # if only one tile is found, this is an error
    if len(att_postpaid_dict) == 1:
        print("Only one device was scraped. Program stopped.")
        driver.quit()
        exit()

    for device in range(len(att_postpaid_dict)):

        # set object's device name
        scraped_postpaid_price.device = att_postpaid_dict[device]['device_name']

        # eliminate pre-owned and non-smartphones
        if 'certified pre-owned' not in scraped_postpaid_price.device and \
                'flip' not in scraped_postpaid_price.device and \
                'wireless' not in scraped_postpaid_price.device and \
                'lg b470' not in scraped_postpaid_price.device and \
                'xp5s' not in scraped_postpaid_price.device and 'url' in att_postpaid_dict[device]:

            # go to url and get storage size
            driver.get(att_postpaid_dict[device]['url'])
            time.sleep(3)
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

                # click on size that was recorded as storage if there is more than one storage size
                if len(soup.findAll('button', class_='preSize')) != 1:

                    # if popup is there, click it and make it go away
                    try:
                        size.click()
                    except WebDriverException:
                        driver.find_element_by_xpath('//*[@id="acsMainInvite"]/a').click()
                        print('popup clicked')
                        size.click()

                    time.sleep(2)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")

                att_scrape_postpaid_promotions(soup, scraped_postpaid_price.url, scraped_postpaid_price.device,
                                               scraped_postpaid_price.storage)

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
                                scraped_postpaid_price.onetime_price = remove_dollar_sign(contract_prices[0].text)
                                scraped_postpaid_price.monthly_price = remove_dollar_sign(contract_prices[1].text)
                            if span.text == 'No annual contract':
                                no_contract_prices = div.findAll('div', class_='attGray text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.retail_price = remove_dollar_sign(no_contract_prices[0].text.replace(',', ''))
                else:
                    for div in soup.findAll('div', class_='row-fluid-nowrap posRel margin-top-5'):
                        for span in div.findAll('span', class_='text-xlarge margin-right-5 adjustLetterSpace ng-binding ng-scope'):
                            if span.text == 'No annual contract':
                                no_contract_prices = div.findAll('div', class_='attOrange text-cramped text-xlarge text-nowrap pad-bottom-10')
                                scraped_postpaid_price.retail_price = remove_dollar_sign(no_contract_prices[0].text)


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




