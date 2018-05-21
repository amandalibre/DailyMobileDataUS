# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from bs4 import BeautifulSoup
import pandas as pd
import datetime

def parser(str):
    str = str.strip()
    str = str.replace("&", ".")
    str = str.replace(" ", "")
    str = str.replace("cents;", "")
    str = str.replace("$", "")
    if "Free" in str:
        str = "Free"
    if ";" in str:
        str = "N/A"
    if "0" in str:
        str = "N/A"
    return str

def brandparser(string):
    string = string.replace(", Phone by Google", "")
    string = string.replace("with Sapphire Shield", "")
    string = string.replace("Samsung", "")
    string = string.replace("Apple", "")
    string = string.replace("6s", "6S")
    string = string.replace("7s", "7S")
    string = string.replace("PLUS", "Plus")
    if "force edition" in string:
        string = "Moto Z2 Force Edition"
    if "Galaxy J3 (2017)" in string:
        string = "Galaxy J3 (2017)"
    if "iPhone X" in string:
        string = "iPhone X"
    if "Galaxy S8 plus" in string:
        string = "Galaxy S8+"
    if "Motorola Moto Z Force Edition 2nd Gen" in string:
        string = "Moto Z2 Force Edition"

    string = removeNonAscii(string)
    string = string.strip()
    return string

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

tmobile_phones = "https://www.t-mobile.com/cell-phones"

tmobile_deals = []
tmobile_devices = []

def main(link):

    driver = webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(link)
    time.sleep(8)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    time.sleep(2)

    devicename = []
    count = 0
    for div in soup.findAll("div", class_="tile col-lg-3 col-md-4 col-sm-6 col-xs-12"):
        for a in soup.findAll("a", class_="m-b-5 product-name text-center regular block ng-binding"):
            devicename.append(brandparser(a.text))
            if devicename[count] not in tmobile_devices:
                tmobile_devices.append(devicename[count])
        for a in div.findAll("a", class_="legal text-magenta ng-binding ng-isolate-scope"):
            if a.text != "":
                tmobile_deals.append([devicename[count], a.text])
        count = count + 1

    today = datetime.date.today()

    datau = pd.DataFrame({"tmobile_deals": tmobile_deals})
    datau.to_csv(r"C:\Users\Amanda Friedman\PycharmProject\VerizonScrapers\Output\out_tmobile_deals_" + str(today) + ".csv", sep=',', encoding='windows=1252', index=False)

    driver.quit()

if __name__ == "__main__":
    main(tmobile_phones)

