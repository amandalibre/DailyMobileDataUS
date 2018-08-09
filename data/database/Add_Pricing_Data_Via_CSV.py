import csv
import datetime
from data.database.Database_Methods import add_postpaid_to_database
from data.database.Add_Postpaid_Pricing_To_Database import remove_postpaid_duplicate
from data.database.Add_Prepaid_Pricing_To_Database import remove_prepaid_duplicate, add_prepaid_pricing_to_database
from data.model.Price import Price, Pre_price

# write payment type (postpaid or prepaid)
payment_type = 'postpaid'

# list providers that need to be uploaded from CSV format
postpaid_providers = ['sprint']
prepaid_providers = ['att']

# global variables
today_filename = datetime.datetime.today().strftime('%m.%d.%Y')
today = datetime.date.today()
time_now = datetime.datetime.now().time()

def get_postpaid_prices_CSV(provider_name):
    prices = []
    empty = 0
    provider_file = r'C:/Users/Amanda Friedman/Documents/Verizon/Daily Tracking Files/VerizonPricingData/' + provider_name + '-postpaid-' + str(today) + '.csv'
    with open(provider_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url = row
            date, time = today, time_now
            if retail_price != '':
                price = Price(provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc, url, date, time)
                prices.append(price)
            else:
                empty += 1
    print("X " + provider_name + " file read, " + str(empty) + " empty rows")
    return prices

def get_prepaid_prices_CSV(provider_name):
    prices = []
    empty = 0
    provider_file = r'C:/Users/Amanda Friedman/Documents/Verizon/Daily Tracking Files/VerizonPricingData/' + provider_name + '-prepaid-' + str(today) + '.csv'
    with open(provider_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            device, storage, price, retail_price, url = row
            date, time = today, time_now
            if retail_price != '':
                pre_price = Pre_price(provider, device, storage, price, retail_price, url, date, time)
                prices.append(pre_price)
            else:
                empty += 1
    print("X " + provider_name + " file read, " + str(empty) + " empty rows")
    return prices


if payment_type == 'postpaid':
    postpaid_prices = {}
    for provider in postpaid_providers:
        postpaid_prices[provider] = get_postpaid_prices_CSV(provider)
        entries = 0
        for price in postpaid_prices[provider]:
            remove_postpaid_duplicate(price.provider, price.device, price.storage, price.date)
            add_postpaid_to_database(price.provider, price.device, price.storage, price.monthly_price,
                                     price.onetime_price, price.retail_price, price.contract_ufc, price.url, price.date, price.time)
            entries += 1
        print(str(entries) + " " + provider + " entries added to database")
    
if payment_type == 'prepaid':
    prepaid_prices = {}
    for provider in prepaid_providers:
        prepaid_prices[provider] = get_prepaid_prices_CSV(provider)
        entries = 0
        for price in prepaid_prices[provider]:
            remove_prepaid_duplicate(price.provider, price.device, price.storage, price.date)
            add_prepaid_pricing_to_database(price.provider, price.device, price.storage, price.price,
                                            price.retail_price, price.url, price.date, price.time)
            entries += 1
        print(str(entries) + ' ' + provider + ' entries added to database')