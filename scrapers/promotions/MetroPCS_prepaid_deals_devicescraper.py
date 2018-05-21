# -*- coding: utf-8 -*-
import datetime
import time
from datetime import timedelta
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException


def parser(string):
    string = string.replace(" 00", ".00")
    return string

def dealscomparison():
    driver = webdriver.Firefox()
    driver.implicitly_wait(5)

    time.sleep(5)
    driver.get("https://www.metropcs.com/shop/phones")
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.close()


    metropcs_dict = {}
    count = 0
    for span in soup.findAll("span", class_="cursor ng-binding"):
        metropcs_dict.update({count: span.text})
        count += 1

    Listprice = []
    Actualprice = []
    Prices = []
    for div in soup.findAll("div", class_="card-content card-price"):
        Prices.append(div.text)
        if "After all offers" in div.text:
            for span in div("span", class_="current-price"):
                Actualprice.append(parser(span.text))
            for span in div("span", class_="normal-price ng-scope"):
                Listprice.append(parser(span.text))
        else:
            for span in div("span", class_="current-price"):
                Actualprice.append(parser(span.text))
                Listprice.append(parser(span.text))

    today = datetime.date.today()
    if today.isoweekday()== 1:
        yesterday = today - timedelta(2)
    else:
        yesterday = today - timedelta(1)
    filename = "out_metropcs_deals-"+str(today) +".csv"
    datau = pd.DataFrame({"Device_name": Devicename, "Actual_price": Actualprice, "List_price": Listprice})
    datau = datau[["Device_name", "Actual_price", "List_price"]]
    datau.to_csv(filename, sep=',', encoding='windows=1251')

    out_today = pd.read_csv("out_metropcs_deals-"+str(today)+".csv")
    today_devices = pd.read_csv("out_metropcs_deals-"+str(today)+".csv")['Device_name'].tolist()
    out_yesterday = pd.read_csv("out_metropcs_deals-"+str(yesterday)+".csv")
    yesterday_devices = pd.read_csv("out_metropcs_deals-"+str(yesterday)+".csv")['Device_name'].tolist()
    if len(today_devices) == len(yesterday_devices):
        if today_devices == yesterday_devices:
            print ('There are no changes to the device order or lineup')
    else:
        newtoday = []
        notheretoday = []
        for device in today_devices:
            if (device not in yesterday_devices):
                newtoday.append(device)
        print("The following devices were added today: "+ str(newtoday))
        for device in yesterday_devices:
            if (device not in today_devices):
                notheretoday.append(device)
        print("The following devices were removed today: " + str(notheretoday))

    def find_changes_in_price(self, out_today, out_yesterday, newtoday):
        changes = []
        for device in out_today:
            if device not in newtoday:
                yesterday_prices = (out_yesterday['Actual_price'], out_yesterday['List_price'])
                today_prices = (out_today['Actual_price'], out_today['List_price'])
                if yesterday_prices == today_prices:
                    changes.append('')
                else:
                    changes.append('CHANGE')
            else:
                changes.append('NEW DEVICE')
        return changes

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

    # driver.close()

if __name__ == "__main__":
    dealscomparison()


