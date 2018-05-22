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

# get T-mobile postpaid device links
tmobile_devices_today = get_postpaid_devices('tmobile', today)

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

for entry in tmobile_devices_today:
    driver.get(entry.url)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # if popup is there, click it and make it go away
    try:
        driver.find_element_by_xpath('//*[@id="acsMainInvite"]/b/b/a').click()
        print('popup clicked')
    except NoSuchElementException:
        print('no popup')

    # make empty list of promotions
    promotions = []

    # upper banner text
    upper_banner_text = driver.find_element_by_id('promo-banner')
    promotions.append(['upper banner', upper_banner_text.text])

    # banner under device name text
    for div2 in soup.findAll("div", class_="text-magenta ng-scope"):
        promotions.append(['banner under device name', div2.text])

    # crossed out text (if savings is anything other than $0.00)
    strike_out_price = soup.findAll('span', class_='text-magenta ng-binding')
    if strike_out_price[0].text != '($0.00 Savings)':
        promotions.append(['discount', strike_out_price[0].text])

    # make object for each promo text instance
    for promo_instance in promotions:
        entry.promo_location = promo_instance[0]
        entry.promo_text = promo_instance[1]
        print(entry.device_name, entry.device_storage, entry.url, entry.promo_location, entry.promo_text)

driver.quit()

