from data.database.Database_Methods import get_scraped_promotions
from data.model.Price import get_day_before
import datetime

today = datetime.date.today()
yesterday = get_day_before(today)

providers = ['verizon', 'att', 'tmobile', 'sprint', 'metropcs', 'cricket']


def changes_report(today, yesterday):
    for provider in providers:

        # get promotions from today and yesterday
        scraped_promotions_today = get_scraped_promotions(provider, today)
        scraped_promotions_yesterday = get_scraped_promotions(provider, yesterday)

        # compare today's device_name (device_storage) to yesterday's
        device_list_today = []
        device_list_yesteday = []
        for promo in scraped_promotions_today:
            if promo.device_name + ' (' + str(promo.device_storage) + ')' not in device_list_today:
                device_list_today.append(promo.device_name + ' (' + str(promo.device_storage) + ')')
        for promo in scraped_promotions_yesterday:
            if promo.device_name + ' (' + str(promo.device_storage) + ')' not in device_list_yesteday:
                device_list_yesteday.append(promo.device_name + ' (' + str(promo.device_storage) + ')')
        added_devices = []
        removed_devices = []
        for device in device_list_today:
            if device not in device_list_yesteday:
                added_devices.append(device)
        for device in device_list_yesteday:
            if device not in device_list_today:
                removed_devices.append(device)
        print(provider.title() + ' removed:')
        print(removed_devices)
        print(provider.title() + ' added:')
        print(added_devices)

        # for each device, check if promo text is the same
        # exception for verizon and sprint postpaid because

changes_report(today, yesterday)



