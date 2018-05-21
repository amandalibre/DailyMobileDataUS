# -*- coding: utf-8 -*-
import datetime
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from time import gmtime, strftime

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
    return string

def brandparsert(string):
    string = string.replace("iPad (9.7-inch)", "iPad")
    string = string.replace("iPad Pro (10.5-inch)", 'iPad Pro 10.5" (64 GB)')
    string = string.replace("iPad Pro (9.7-inch)", 'iPad Pro 9.7"')
    string = string.replace("Samsung", "")
    string = string.replace("iPad mini 4 - 128GB", "iPad mini 4")
    string = string.replace("Galaxy Tab E", 'Galaxy Tab E 8"')
    # string = string.replace("Motorola", "")
    string = string.replace("Apple", "")
    string = string.replace("6s", "6S")
    string = string.replace("7s", "7S")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    if "Galaxy J3 (2017)" in string:
        string = "Galaxy J3 (2017)"
    string = removeNonAscii(string)
    string = string.strip()
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x) < 128, s))

att_phones = "https://www.att.com/shop/wireless/devices/smartphones.html"

att_deals = {}
att_devices = []

def main(link):
    print("Start time: ", strftime("%H:%M:%S", gmtime()))
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(link)

    time.sleep(15)
    driver.find_element_by_id("deviceShowAllLink").click()

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    deal_teasers = []
    device_links = []
    for div in soup.findAll("div", class_="list-item xref"):
        for a in div.findAll("a", class_=" titleURLchng"):
            att_devices.append(brandparser(parser(a.text)))
        if len(div.findAll("div", class_="holidayFlag")) == 2:
            deal_teaser = div.findAll("div", class_="holidayFlag")[1].img['title']
            deal_teasers.append(deal_teaser)
        else:
            deal_teasers.append("N/A")
        for a in div.findAll("a", class_="clickStreamSingleItem imageURLchng"):
            device_link = a['href']
            device_links.append(device_link)

    count = 0
    for device in att_devices:
        att_deals[device] = {'deal_teaser': deal_teasers[count], 'device_link': "https://www.att.com" + device_links[count],
                             'device_price_link': "https://www.att.com/shop/wireless/deviceconfigurator.html?prefetched=true&sku=" + device_links[count].split('=', 1)[1]}
        count = count + 1

    for key, value in att_deals.items():
        driver.implicitly_wait(3)
        driver.get(value['device_link'])
        time.sleep(10)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        att_deals[key]['deals'] = []
        for span in soup.findAll("span", class_="offerTxt"):
            if span.text.strip() != '':
                banner = span.text.strip()
                att_deals[key]['deals'].append(banner)
        for div in soup.findAll("div", class_="ds2MarketingMessageTextStyle"):
            att_deals[key]['deals'].append(div.text)

    if len(att_deals) == 1:
        print("Only one device was scraped. Program stopped.")
        driver.quit()
        exit()

    today = datetime.date.today()

    df = pd.DataFrame(columns=['devices', 'deals'])
    for device in att_devices:
        df = df.append({'devices': device, 'deals': att_deals[device]['deals']}, ignore_index=True)
        df.to_csv(r"C:\Users\Amanda Friedman\PycharmProject\VerizonScrapers\Output\out_att_deals_" + str(today) + ".csv", sep=',', encoding='windows=1252', index=False)

    print("End time: ", strftime("%H:%M:%S", gmtime()))

    driver.quit()

if __name__ == "__main__":
    main(att_phones)