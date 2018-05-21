import pymysql.cursors
from data.model.Calendar_deal import Calendar_deal
from data.model.Price import Price, Pre_price

def add_to_database(database, provider, category, deal_id, devices, promotion_details, promotion_summary, url, status,
                    modified_summary, date, homepage, start_date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    if database == "daily_promotions":
        query = "insert into daily_promotions(provider, category, deal_id, devices, promotion_details, promotion_summary, url, status, modified_summary, date, homepage, start_date) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    elif database == "historical_promotions":
        query = "insert into historical_promotions(provider, category, deal_id, devices, promotion_details, promotion_summary, url, status, modified_summary, date, homepage, start_date) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    args = (provider, category, deal_id, devices, promotion_details, promotion_summary, url, status,
            modified_summary, date, homepage, start_date)
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query, args)
        cursor.close()
    finally:
        connection.commit()
        connection.close()
        
def add_postpaid_to_database(provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    
    query = "insert into postpaid(provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    args = (provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time)
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        cursor.close()
    finally:
        connection.commit()
        connection.close()


def check_duplicates(database, deal_id, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    if database == "daily_promotions":
        query = "SELECT COUNT(1) FROM daily_promotions WHERE deal_id = %s AND date = %s;"
    elif database == "historical_promotions":
        query = "SELECT COUNT(1) FROM historical_promotions WHERE deal_id = %s AND date = %s;"
    args = (deal_id, date)
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query, args)
        duplicate = cursor.fetchone()[0]
        if duplicate == 0:
            return False
        else:
            return True
    finally:
        connection.close()

def remove_yesterday(day_before, deal_id):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query1 = "SELECT status FROM historical_promotions WHERE deal_id = %s AND date = %s;"
    query2 = "DELETE FROM historical_promotions WHERE deal_id = %s AND date = %s;"
    args = (deal_id, day_before)
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query1, args)
        yesterday_status = cursor.fetchone()
        if yesterday_status != None:
            yesterday_status = yesterday_status[0]
            if yesterday_status == 'no change' or yesterday_status == 'new':
                cursor.execute(query2, args)
                cursor.close()
    finally:
        connection.commit()
        connection.close()

def edit_yesterday(day_before, deal_id, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "UPDATE historical_promotions SET status='discontinued' WHERE deal_id = %s AND date = %s;"
    args = (deal_id, day_before)
    query2 = "UPDATE historical_promotions SET start_date=%s, status='no change' WHERE deal_id = %s AND date = %s;"
    args2 = (date, deal_id, date)
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query, args)
        cursor.execute(query2, args2)
        cursor.close()
    finally:
        connection.commit()
        connection.close()

def get_calendar_deals(provider, category):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT provider, category, deal_id, devices, promotion_details, promotion_summary, url, status, " \
            "modified_summary, date, homepage, start_date FROM historical_promotions WHERE provider = %s AND category = %s;"
    args = provider, category
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query, args)
        deal_objs = []
        for deal in cursor.fetchall():
            deal_obj = Calendar_deal(deal[0], deal[1], deal[2], deal[3], deal[4], deal[5], deal[6], deal[7], deal[8],
                                     deal[9], deal[10], deal[11])
            deal_objs.append(deal_obj)
        cursor.close()
        return deal_objs
    finally:
        connection.commit()
        connection.close()

def get_postpaid_device_prices(provider, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time" \
            " FROM postpaid WHERE provider = %s AND date = %s;"
    args = provider, date
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        price_objs = []
        for price in cursor.fetchall():
            price_obj = Price(price[0], price[1], price[2], price[3], price[4], price[5], price[6], price[7], price[8], price[9])
            price_objs.append(price_obj)
        cursor.close()
        return price_objs
    finally:
        connection.commit()
        connection.close()

def get_postpaid_device_prices_yesterday(provider, device, storage, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT monthly_price, onetime_price, retail_price" \
            " FROM postpaid WHERE provider = %s AND device = %s AND storage = %s AND date = %s LIMIT 1;"
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
            cursor.close()
            return yesterday_monthly, yesterday_onetime, yesterday_retail
    finally:
        connection.commit()
        connection.close()

def get_prepaid_device_prices(provider, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT provider, device, storage, price, retail_price, url, date, time" \
            " FROM prepaid WHERE provider = %s AND date = %s;"
    args = provider, date
    try:
        cursor = connection.cursor()
        cursor.execute('USE pricing')
        cursor.execute(query, args)
        pre_price_objs = []
        for price in cursor.fetchall():
            pre_price_obj = Pre_price(price[0], price[1], price[2], price[3], price[4], price[5], price[6], price[7])
            pre_price_objs.append(pre_price_obj)
        cursor.close()
        return pre_price_objs
    finally:
        connection.commit()
        connection.close()

def get_prepaid_device_prices_yesterday(provider, device, storage, date):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query = "SELECT price, retail_price" \
            " FROM prepaid WHERE provider = %s AND device = %s AND storage = %s AND date = %s LIMIT 1;"
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

