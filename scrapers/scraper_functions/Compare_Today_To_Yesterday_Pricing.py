from data.database.Database_Methods import get_postpaid_device_prices, get_postpaid_device_prices_yesterday, get_prepaid_device_prices, get_prepaid_device_prices_yesterday
from data.model.Price import get_day_before
import datetime

today = datetime.date.today()
yesterday = get_day_before(today)

postpaid_providers = ['verizon', 'att', 'tmobile', 'sprint', 'xfinity']
prepaid_providers = ['verizon', 'att', 'metropcs', 'cricket']


def compare_today_to_yesterday_report(today, yesterday):
    print('Prepaid:')
    for provider in prepaid_providers:
        prepaid_prices_today = get_prepaid_device_prices(provider, today)
        prepaid_prices_yesterday = get_prepaid_device_prices(provider, yesterday)
        device_list_today = []
        device_list_yesteday = []
        for price in prepaid_prices_today:
            device_list_today.append(price.device + ' (' + price.storage + ')')
        for price_yesterday in prepaid_prices_yesterday:
            device_list_yesteday.append(price_yesterday.device + ' (' + price_yesterday.storage + ')')
        for device_today in device_list_today:
            if device_today not in device_list_yesteday:
                print(provider.title() + ' added the ' + device_today)
        for device_yesterday in device_list_yesteday:
            if device_yesterday not in device_list_today:
                print(provider.title() + ' removed the ' + device_yesterday)
        for price in prepaid_prices_today:
            if price.price_change == 'yes' and price.device + ' (' + price.storage + ')' in device_list_yesteday:
                print(provider.title() + ' ' + price.device + ' (' + price.storage + '): price changed from ' + str(price.yesterday_price) + ' to ' + str(price.retail_price))

    print('Postpaid:')
    for provider in postpaid_providers:
        postpaid_prices_today = get_postpaid_device_prices(provider, today)
        postpaid_prices_yesterday = get_postpaid_device_prices(provider, yesterday)
        device_list_today = []
        device_list_yesteday = []
        for price in postpaid_prices_today:
            device_list_today.append(price.device + ' (' + price.storage + ')')
        for price_yesterday in postpaid_prices_yesterday:
            device_list_yesteday.append(price_yesterday.device + ' (' + price_yesterday.storage + ')')
        for device_today in device_list_today:
            if device_today not in device_list_yesteday:
                print(provider.title() + ' added the ' + device_today)
        for device_yesterday in device_list_yesteday:
            if device_yesterday not in device_list_today:
                print(provider.title() + ' removed the ' + device_yesterday)
        for price in postpaid_prices_today:
            if price.monthly_price_change == 'yes' and price.device + ' (' + price.storage + ')' in device_list_yesteday:
                print(provider.title() + ' ' + price.device + ' (' + price.storage + '): monthly price changed from ' + str(price.yesterday_monthly) + ' to ' + str(price.monthly_price))
            if price.retail_price_change == 'yes' and price.device + ' (' + price.storage + ')' in device_list_yesteday:
                print(provider.title() + ' ' + price.device + ' (' + price.storage + '): retail price changed from ' + str(price.yesterday_retail) + ' to ' + str(price.retail_price))
            if price.onetime_price_change == 'yes' and price.device + ' (' + price.storage + ')' in device_list_yesteday:
                print(provider.title() + ' ' + price.device + ' (' + price.storage + '): onetime price changed from ' + str(price.yesterday_onetime) + ' to ' + str(price.onetime_price))


compare_today_to_yesterday_report(today, yesterday)



