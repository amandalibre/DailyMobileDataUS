import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from data.model.Scraped_Postpaid_Price import ScrapedPostpaidPrice

# make object
scraped_postpaid_price = ScrapedPostpaidPrice()

# set hardcoded variables
scraped_postpaid_price.date = datetime.date.today()
scraped_postpaid_price.time = datetime.datetime.now().time()
scraped_postpaid_price.provider = 'att'

# get skus from device landing page
# headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver = os.getcwd() + "\\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)
driver.implicitly_wait(5)

# go to website
driver.get('https://www.att.com/shop/wireless/devices/cellphones.html')
time.sleep(2)

# check if all devices are shown on page
devices_shown = driver.find_element_by_class_name('deviceCount').text.split(' ')[-1]
devices_total = driver.find_element_by_class_name('deviceSize').text
if devices_shown != devices_total:
    # click 'Show All' button if it exists
    driver.find_element_by_id("deviceShowAllLink").click()

# load page and get soup
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
driver.quit()

# make list of skus
sku_list = [item["id"].replace("item_", "") for item in soup.findAll("div", {"class": "list-item xref"})]

sku_list.remove("sku9030294")

# iterate through skus
for sku in sku_list:

    print(" ")
    print("https://www.att.com/services/shopwireless/model/att/ecom/api/DeviceDetailsActor/getDeviceProductDetails?ctnList=&fanNumber=&includeAssociatedProducts=true&includePrices=true&skuId=" + sku)

    time.sleep(2)

    # try:

    # get json
    plan_page = requests.get(r"https://www.att.com/services/shopwireless/model/att/ecom/api/DeviceDetailsActor/getDeviceProductDetails?ctnList=&fanNumber=&includeAssociatedProducts=true&includePrices=true&skuId=" + sku)
    time.sleep(2)
    plan_soup = BeautifulSoup(plan_page.text, 'html.parser')
    att_json = json.loads(plan_soup.text)

    manufacturer = att_json["result"]["methodReturnValue"]["manufacturer"]

    sizes = []

    items = att_json["result"]["methodReturnValue"]["skuItems"]

    for skuItem in items:
        if not items[skuItem]["devicePageURL"]:
            print("no devicePageURL")
            continue

        scraped_postpaid_price.storage = items[skuItem]["size"]
        if scraped_postpaid_price.storage in sizes:
            continue
        else:
            sizes.append(scraped_postpaid_price.storage)

        print(items[skuItem]["model"])
        scraped_postpaid_price.device = items[skuItem]["model"]
        if manufacturer != "Samsung" and manufacturer != "Apple" and manufacturer != "Motorola":
            scraped_postpaid_price.device = manufacturer + " " + scraped_postpaid_price.device

        scraped_postpaid_price.url = "https://www.att.com" + items[skuItem]["devicePageURL"]

        for price in items[skuItem]["priceList"]:
            if price["leaseTotalMonths"] == 24:
                scraped_postpaid_price.monthly_price = price["dueMonthlyLeasePrice"]
                scraped_postpaid_price.retail_price = price["noCommitmentTermPrice"]
                scraped_postpaid_price.onetime_price = price["dueTodayLease"]

        print(scraped_postpaid_price.provider, scraped_postpaid_price.device,
              scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
              scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
              scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
              scraped_postpaid_price.date, scraped_postpaid_price.time)

            # remove_postpaid_duplicate(scraped_postpaid_price.provider, scraped_postpaid_price.device,
            #                           scraped_postpaid_price.storage, scraped_postpaid_price.date)
            # add_postpaid_to_database(scraped_postpaid_price.provider, scraped_postpaid_price.device,
            #                          scraped_postpaid_price.storage, scraped_postpaid_price.monthly_price,
            #                          scraped_postpaid_price.onetime_price, scraped_postpaid_price.retail_price,
            #                          scraped_postpaid_price.contract_ufc, scraped_postpaid_price.url,
            #                          scraped_postpaid_price.date, scraped_postpaid_price.time)
    #
    # except ValueError:
    #     print("error with JSON")
