import csv
import datetime

import pymysql.cursors

from data.model.Deal import Deal

deals_by_provider = {}
all_deals_dict = {}
NUM_PROVIDERS = 6
provider_names = ['verizon', 'att', 'tmobile', 'sprint', 'metropcs', 'cricket']
provider_names_email = ['Verizon', 'AT&T', 'T-Mobile', 'Sprint', 'MetroPCS', 'Cricket']
today = datetime.date.today()
day_of_week = datetime.timedelta(today.weekday())
today_header = datetime.datetime.today().strftime('%m/%d/%Y')
today_cover = datetime.datetime.today().strftime('%B' + ' ' + '%d' + ', ' + '%Y')
today_filename = datetime.datetime.today().strftime('%m.%d.%Y')
today_deal_id = datetime.datetime.today().strftime('%m%d%Y')
day_of_week = datetime.timedelta(today.weekday())
deals = []

provider_file1 = r'C:/Users/Amanda Friedman/Documents/Verizon/Daily Tracking Files/VerizonPromotionsData/BogoHistorical_test.csv'
provider_file2 = r'C:/Users/Amanda Friedman/Documents/Verizon/Daily Tracking Files/VerizonPromotionsData/BogoHistorical_test_nextday.csv'
provider_file3 = r'C:/Users/Amanda Friedman/Documents/Verizon/Daily Tracking Files/VerizonPromotionsData/BogoHistorical.csv'

def get_day_before(today):
    if day_of_week == 0:
        day_before = today - datetime.timedelta(days=2)
    else:
        day_before = today - datetime.timedelta(days=1)
    return day_before

def get_deals(provider_file):
    with open(provider_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            provider, category, deal_id, devices, promotion_details, promotion_summary, url, status, modified_summary, date, homepage = row
            # filename_provider, filename_date = provider_name, str(today)
            filename_provider, filename_date = "N/A", str(today)
            deal = Deal(provider, category, deal_id, devices, promotion_details, promotion_summary, url, status,
                        modified_summary, date, homepage, filename_provider, filename_date)
            deals.append(deal)
    return deals

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

def remove_yesterday(day_before, deal_id, rem_count):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query1 = "SELECT status FROM historical_promotions WHERE deal_id = %s AND date < %s LIMIT 1;"
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
                rem_count += 1
                cursor.execute(query2, args)
                cursor.close()
                return rem_count
    finally:
        connection.commit()
        connection.close()

def edit_yesterday(day_before, deal_id, mod_count):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 port=3306,
                                 password='123456',
                                 charset='utf8')

    query1 = "SELECT status FROM historical_promotions WHERE deal_id = %s AND date = %s;"
    query2 = "UPDATE historical_promotions SET status = 'discontinued' WHERE deal_id = %s AND date = %s;"
    args = (deal_id, day_before)
    try:
        cursor = connection.cursor()
        cursor.execute('USE promotions')
        cursor.execute(query1, args)
        yesterday_status = cursor.fetchone()
        if yesterday_status != None:
            yesterday_status = yesterday_status[0]
            if yesterday_status == 'no change' or yesterday_status == 'new':
                mod_count += 1
                cursor.execute(query2, args)
                cursor.close()
                return mod_count
    finally:
        connection.commit()
        connection.close()

# get_deals(provider_file1)
# get_deals(provider_file2)
get_deals(provider_file3)

daily_count = 0
hist_count = 0
rem_count = 0
mod_count = 0
for deal in deals:
    if check_duplicates("daily_promotions", deal.deal_id, deal.date_mysql) == False:
        daily_count += 1
        add_to_database("daily_promotions", deal.provider, deal.category, deal.deal_id, deal.devices, deal.promotion_details,
                        deal.promotion_summary, deal.url, deal.status, deal.modified_summary, deal.date_mysql, deal.homepage,
                        deal.start_date_mysql)
    if check_duplicates("historical_promotions", deal.deal_id, deal.date_mysql) == False:
        hist_count += 1
        add_to_database("historical_promotions", deal.provider, deal.category, deal.deal_id, deal.devices, deal.promotion_details,
                    deal.promotion_summary, deal.url, deal.status, deal.modified_summary, deal.date_mysql, deal.homepage,
                    deal.start_date_mysql)
    day_before = get_day_before(today)
    if deal.status != 'modified':
        remove_yesterday(day_before, deal.deal_id, rem_count)
    else:
        edit_yesterday(day_before, deal.deal_id, mod_count)
print(daily_count, "deals added to daily database &", len(deals) - daily_count, "duplicates ignored.")
print(hist_count, "deals added, ", rem_count, " old entries removed & ", mod_count, " pre-modified entries edited in historical database &",
      len(deals) - hist_count, "duplicate ignored.")