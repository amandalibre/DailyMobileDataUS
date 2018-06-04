import datetime
import csv
import pymysql

day_of_week = datetime.datetime.today().weekday()
today = datetime.date.today()

def get_day_before(today):
    if day_of_week == 0:
        day_before = today - datetime.timedelta(days=2)
    else:
        day_before = today - datetime.timedelta(days=1)
    return day_before


approved_device_list = []
tablet_list = []
flagship_list = []
flipphone_list = []
def get_master_device_list():
    provider_file = r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Master Device List\Device List.csv'
    with open(provider_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            device, is_tablet, is_flagship, is_flipphone = row[0], row[1], row[2], row[3]
            device = device.strip()
            approved_device_list.append(device)
            if is_tablet == 'yes':
                tablet = device.strip()
                tablet_list.append(tablet)
            if is_flagship == 'yes':
                flagship = device.strip()
                flagship_list.append(flagship)
            if is_flipphone == 'yes':
                flipphone = device.strip()
                flipphone_list.append(flipphone)
    return approved_device_list, tablet_list, flagship_list, flipphone_list

def get_postpaid_device_prices_yesterday(provider, device, storage, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT monthly_price, onetime_price, retail_price, contract_ufc" \
            " FROM postpaid WHERE provider = %s AND device = %s AND storage = %s AND date = %s " \
            "AND time < '10:30:00' LIMIT 1;"
    args = provider, device, storage, date
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        yesterday = cursor.fetchone()
        if yesterday is None:
            return None
        else:
            yesterday = list(yesterday)
            yesterday_monthly = yesterday[0]
            yesterday_onetime = yesterday[1]
            yesterday_retail = yesterday[2]
            yesterday_contract_ufc = yesterday[3]
            cursor.close()
            return yesterday_monthly, yesterday_onetime, yesterday_retail, yesterday_contract_ufc
    finally:
        connection.commit()
        connection.close()

class Price():

    def __init__(self, provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time):
        self.provider = provider
        self.device = device.strip()
        approved_devices_list, tablets_list, flagships_list, flipphones_list = get_master_device_list()
        if device in tablets_list:
            self.is_tablet = 'yes'
        else:
            self.is_tablet = 'no'
        if device in flipphones_list:
            self.is_flipphone = 'yes'
        else:
            self.is_flipphone = 'no'
        if device.lower().strip() not in approved_devices_list:
            print('Error (postpaid): ' + device + ' not in master_device_list')
        self.storage = storage
        self.monthly_price = monthly_price
        self.onetime_price = onetime_price
        self.retail_price = retail_price
        self.contract_ufc = contract_ufc
        self.url = url
        self.date = date
        self.time = time
        if get_postpaid_device_prices_yesterday(self.provider, self.device, self.storage, get_day_before(today)) is None:
            self.monthly_price_change = 'yes'
            self.onetime_price_change = 'yes'
            self.retail_price_change = 'yes'
            self.contract_ufc_change = 'yes'
        else:
            yesterday_monthly, yesterday_onetime, yesterday_retail, yesterday_contract_ufc = get_postpaid_device_prices_yesterday(self.provider, self.device, self.storage, get_day_before(today))
            if yesterday_monthly == monthly_price:
                self.monthly_price_change = 'no'
            else:
                self.monthly_price_change = 'yes'
                self.yesterday_monthly = yesterday_monthly
            if yesterday_onetime == onetime_price:
                self.onetime_price_change = 'no'
            else:
                self.onetime_price_change = 'yes'
                self.yesterday_onetime = yesterday_onetime
            if yesterday_retail == retail_price:
                self.retail_price_change = 'no'
            else:
                self.retail_price_change = 'yes'
                self.yesterday_retail = yesterday_retail
            if yesterday_contract_ufc == contract_ufc:
                self.contract_ufc_change = 'no'
            else:
                self.contract_ufc_change = 'yes'
                self.yesterday_contract_ufc = yesterday_contract_ufc

def get_prepaid_device_prices_yesterday(provider, device, storage, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT price" \
            " FROM prepaid WHERE provider = %s AND device = %s AND storage = %s AND date = %s " \
            "AND time < '10:30:00' LIMIT 1;"
    args = provider, device, storage, date
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        yesterday = cursor.fetchone()
        if yesterday is None:
            return None
        else:
            yesterday = list(yesterday)
            yesterday_price = yesterday[0]
            cursor.close()
            return yesterday_price
    finally:
        connection.commit()
        connection.close()

class Pre_price():

    def __init__(self, provider, device, storage, price, retail_price, url, date, time):
        self.provider = provider
        self.device = device.strip()
        approved_devices_list, tablets_list, flagships_list, flipphones_list = get_master_device_list()
        if device.lower().strip() not in approved_devices_list:
            print('Error (prepaid): ' + device.lower() + ' not in master_device_list')
        if device.lower().strip() in flipphones_list:
            self.is_flipphone = 'yes'
        else:
            self.is_flipphone = 'no'
        self.storage = storage
        self.price = price
        self.retail_price = retail_price
        self.url = url
        self.date = date
        self.time = time
        if get_prepaid_device_prices_yesterday(self.provider, self.device, self.storage, get_day_before(today)) is None:
            self.price_change = 'yes'
        else:
            yesterday_price = get_prepaid_device_prices_yesterday(self.provider, self.device, self.storage, get_day_before(today))
            if yesterday_price == self.price:
                self.price_change = 'no'
            else:
                self.price_change = 'yes'
                self.yesterday_price = yesterday_price

