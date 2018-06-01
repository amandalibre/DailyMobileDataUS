# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from data.database.Database_Methods import get_postpaid_devices, add_scraped_promotions_to_database
import os


def ver_scrape_postpaid_promotions():
    # date
    date = datetime.date.today()

    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # get Verizon postpaid device links
    devices_today_all_sizes = get_postpaid_devices('verizon', date)

    # make list of device names and new list with only one size per each device
    device_names_today = []
    devices_today = []
    for entry in devices_today_all_sizes:
        if entry.device_name not in device_names_today:
            devices_today.append(entry)
            device_names_today.append(entry.device_name)

    # iterate through unique links
    for entry in devices_today:
        driver.get(entry.url)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # DEVICE PAGE LEVEL
        # make empty list of promotions
        promotions = []

        # # upper banner text (doesn't change by payment option)
        # upper_banner_text = driver.find_element_by_class_name('pointer')
        # if upper_banner_text.text.strip() != '':
        #     promotions.append(['upper banner', upper_banner_text.text.strip()])

        # alternate way to get banner text
        upper_banner_text_2 = driver.find_element_by_class_name('clearfix')
        if upper_banner_text_2.text.strip() != '':
            promotions.append(['upper banner', upper_banner_text_2.text.strip()])

        # crossed out price
        pricing_options = soup.findAll('div', class_='pad8 noRightPad')
        for div in pricing_options:
            if 'was' in div.text:
                promotions.append(['crossed out price', div.text.replace('2-Year Contract', ' 2-Year Contract').replace('24 Monthly Payments',' 24 Monthly Payments').replace('was ', ' was')])

        # check if device is out of stock
        if soup.find('div', class_='row pdpReviews').text == 'No longer available for purchase.':
            promotions.append('out of stock', 'out of stock')

        else:

            # select each device size
            size_button_pad = soup.find('div', class_='displayFlex rowNoWrap priceSelectorRow')
            size_buttons = size_button_pad.findAll('div', class_='grow1basis0 priceSelectorColumn radioGroup positionRelative')
            for size_button_number in range(1, len(size_buttons) + 1):

                # SIZE LEVEL

                # record new device size
                entry.device_storage = size_buttons[size_button_number - 1].text.replace('GB', '')

                # click on different storage size to show device size-specific promos
                # if popup is there, remove it before clicking
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(
                            size_button_number) + ']/div/div/p').click()
                except WebDriverException:
                    driver.find_element_by_class_name('fsrCloseBtn').click()
                    print('popup clicked')
                    driver.find_element_by_xpath(
                        '//*[@id="tile_container"]/div[1]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div/div[' + str(
                            size_button_number) + ']/div/div/p').click()
                time.sleep(2)

                # each payment option has its own banners
                for option in range(1, len(pricing_options) + 1):
                    option_button = driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/div/div[' + str(option) + ']/div/div/div')

                    # PAYMENT LEVEL
                    # click on different payment options to show different promos
                    # if popup is there, remove it before clicking
                    try:
                        option_button.click()
                    except WebDriverException:
                        driver.find_element_by_class_name('fsrCloseBtn').click()
                        print('popup clicked')
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

                    # hardcoded variables
                    entry.date = datetime.date.today()
                    entry.time = datetime.datetime.now().time()
                    entry.provider = 'verizon'

                    # # print results
                    # print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

                    # add to database
                    add_scraped_promotions_to_database(entry.provider, entry.device_name, entry.device_storage,
                                                       entry.promo_location, entry.promo_text, entry.url, entry.date,
                                                       entry.time)

    driver.quit()


