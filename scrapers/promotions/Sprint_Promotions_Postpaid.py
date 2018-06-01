# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from data.database.Database_Methods import get_postpaid_devices, add_scraped_promotions_to_database
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def spr_scrape_postpaid_promotions():
    # date
    date = datetime.date.today()

    # headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_driver = os.getcwd() + "\\chromedriver.exe"

    # headless Chrome
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
    driver.implicitly_wait(5)

    # get Sprint postpaid device links
    devices_today_all_sizes = get_postpaid_devices('sprint', date)

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

        # iterate through sizes
        selector = driver.find_element_by_id('sprint_storage_selector')
        selector.click()
        time.sleep(2)
        sizes = selector.text.strip().replace(' GB', '')
        sizes = sizes.split('\n')

        # iterate through sizes
        for size in sizes:

            # click on size and reload page
            select = Select(driver.find_element_by_id('sprint_storage_selector'))
            select.select_by_value(size)
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # record device size
            entry.device_storage = size

            # make empty list of promotions
            promotions = []

            # upper banner text (not all pages have banners)
            try:
                upper_banner_text = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div/div/div/div')
                promotions.append(['upper banner', upper_banner_text.text.strip()])
            except NoSuchElementException:
                print('no upper banner')

            # promotion text under price box
            price_boxes = soup.findAll('div', class_='col-xs-24 col-lg-24 col-xl-24 mb-20 active')
            for box in price_boxes:
                if box.find('strong',
                            class_='display-block font-size-16 font-size-md-18 color--blue').text != ' Full price':
                    for li in box.findAll('li', class_='promo-item'):
                        promotions.append(['banner under Sprint Flex box', li.text.replace('Detail', '').strip()])

            # crossed out price
            strike_out_price = soup.findAll('del', class_='sprint-price-del')
            if strike_out_price[0].text != '':
                promotions.append(['crossed out price', strike_out_price[0].text])

            # make object for each promo text instance
            for promo_instance in promotions:
                entry.promo_location = promo_instance[0]
                entry.promo_text = promo_instance[1]

                # time variables
                entry.date = datetime.date.today()
                entry.time = datetime.datetime.now().time()
                entry.provider = 'sprint'

                # print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)
                add_scraped_promotions_to_database(entry.provider, entry.device_name, entry.device_storage,
                                                   entry.promo_location, entry.promo_text, entry.url, entry.date, entry.time)

    driver.quit()

