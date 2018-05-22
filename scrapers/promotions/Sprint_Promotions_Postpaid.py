# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from data.database.Database_Methods import get_postpaid_devices
import os
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() +"\\chromedriver.exe"
today = datetime.date.today()

# get Sprint postpaid device links
sprint_devices_today = get_postpaid_devices('sprint', today)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

for entry in sprint_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

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
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

driver.quit()

