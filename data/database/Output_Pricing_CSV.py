import csv
from data.database.Database_Methods import get_prepaid_device_prices, get_postpaid_device_prices

# type provider name in lower case
provider = 'sprint'
# type prepaid or postpaid (if both do two separately) in lower case
plan_type = 'postpaid'
# type last available date to pull date from in YYYY-MM-DD format
date = '2018-06-14'

if plan_type == 'postpaid':
    data_for_csv = get_postpaid_device_prices(provider, date)
    with open(r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\CSV files\DB-'+provider+'-'+plan_type+'-'+date+'.csv', 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['device', 'storage', 'monthly_price', 'onetime_price', 'retail_price',  'contract_ufc', 'url'])
        for price in data_for_csv:
            writer.writerow([price.device, price.storage, price.monthly_price, price.onetime_price, price.retail_price, price.contract_ufc, price.url])

if plan_type == 'prepaid':
    data_for_csv = get_prepaid_device_prices(provider, date)
    with open(r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\CSV files\DB-'+provider+'-'+plan_type+'-'+date+'.csv', 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(['device', 'storage', 'price', 'retail_price', 'url'])
        for price in data_for_csv:
            writer.writerow([price.device, price.storage, price.price, price.retail_price, price.url])
