# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_postpaid_devices, add_scraped_promotions_to_database
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"

# time variables
date = datetime.date.today()
time_now = datetime.datetime.now().time()

# get Verizon postpaid device links
verizon_devices_today = get_postpaid_devices('verizon', date)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

def remove_popup():
    try:
        driver.find_element_by_class_name('fsrCloseBtn').click()
        print('popup clicked')
    except NoSuchElementException:
        print('no popup')

for entry in verizon_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # make empty list of promotions
    promotions = []

    # upper banner text (doesn't change by payment option)
    upper_banner_text = driver.find_element_by_class_name('pointer')
    promotions.append(['upper banner', upper_banner_text.text.strip()])

    # crossed out price
    pricing_options = soup.findAll('div', class_='pad8 noRightPad')
    for div in pricing_options:
        if 'was' in div.text:
            promotions.append(['crossed out price', div.text.replace('2-Year Contract', ' 2-Year Contract').replace('24 Monthly Payments',' 24 Monthly Payments').replace('was ', ' was')])

    # select each device size
    size_button_pad = soup.find('div', class_='displayFlex rowNoWrap priceSelectorRow')
    size_buttons = size_button_pad.findAll('div', class_='grow1basis0 priceSelectorColumn radioGroup positionRelative')
    for size_button_number in range(1, len(size_buttons) + 1):

        # record new device size
        entry.device_storage = size_buttons[size_button_number - 1].text.replace('GB', '')

        # remove popup before clicking
        remove_popup()

        # click on different storage size to show device size-specific promos
        driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(size_button_number) + ']/div/div/p').click()
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # each payment option has its own banners
        for option in range(1, len(pricing_options) + 1):
            option_button = driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/div/div[' + str(option) + ']/div/div/div')

            # remove popup before clicking
            remove_popup()

            # click on different payment options to show different promos
            option_button.click()
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # promotion text above device icon
            try:
                banner_above_icon = soup.find('div', class_='offersPad fontSize_12 lineHeight8')
                promotions.append(['banner above device icon', banner_above_icon.text.replace('Special Offer', '').replace('See the details', '').replace('\n', '')])
            except AttributeError:
                print('no banner above device icon')

            # banner under price
            below_price_banner = soup.find('div', class_='row padTop6 noSideMargin priceLabel').text
            if below_price_banner != 'Retail Price' and below_price_banner != 'Early Termination Fee: $175 (2-Year Contracts)':
                promotions.append(['banner below price', below_price_banner])

        # make object for each promo text instance
        for promo_instance in promotions:
            entry.promo_location = promo_instance[0]
            entry.promo_text = promo_instance[1]
            entry.date = date
            entry.time = time_now
            entry.provider = 'verizon'
            print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)
            add_scraped_promotions_to_database(entry.provider, entry.device_name, entry.device_storage,
                                               entry.promo_location, entry.promo_text, entry.url, entry.date,
                                               entry.time)

driver.quit()

