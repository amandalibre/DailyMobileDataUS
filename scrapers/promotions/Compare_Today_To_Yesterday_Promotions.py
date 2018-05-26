from data.database.Database_Methods import get_scraped_promotions
from data.model.Price import get_day_before
import datetime
import xlsxwriter

today = datetime.date.today()
yesterday = get_day_before(today)

providers = ['verizon', 'att', 'tmobile', 'sprint', 'metropcs', 'cricket']


def changes_report(today, yesterday):
    for provider in providers:

        # get promotions from today and yesterday
        scraped_promotions_today = get_scraped_promotions(provider, today)
        scraped_promotions_yesterday = get_scraped_promotions(provider, yesterday)

        # make empty lists for devices today and yesterday
        device_list_today = []
        device_list_yesteday = []

        # make list of all unique device/storage combinations for today and yesterday
        for promo in scraped_promotions_today:
            if promo.device_name + ' (' + str(promo.device_storage) + ')' not in device_list_today:
                device_list_today.append(promo.device_name + ' (' + str(promo.device_storage) + ')')
        for promo in scraped_promotions_yesterday:
            if promo.device_name + ' (' + str(promo.device_storage) + ')' not in device_list_yesteday:
                device_list_yesteday.append(promo.device_name + ' (' + str(promo.device_storage) + ')')

        # make empty list of devices that were addd today and devices that were removed today
        added_devices = []
        removed_devices = []

        # iterate lists to see what changed
        for device in device_list_today:
            if device not in device_list_yesteday:
                added_devices.append(device)
        for device in device_list_yesteday:
            if device not in device_list_today:
                removed_devices.append(device)

        # create list of what was removed today
        set1 = set((promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) for promo in scraped_promotions_today)
        removed = [promo for promo in scraped_promotions_yesterday if (promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) not in set1]

        # create list of what was added today
        set2 = set((promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) for promo in scraped_promotions_yesterday)
        added = [promo for promo in scraped_promotions_today if (promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) not in set2]

        scraped_promos_today_plus_discontinued = scraped_promotions_today + removed
        scraped_promos_today_plus_discontinued.sort(key=lambda promo: promo.device_name, reverse=True)

        # Create an Excel workbook and add worksheet
        workbook = xlsxwriter.Workbook(r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Promo Change Report\_' + provider.title() + '_Promo_Change_Report_' + str(today) +'.xlxs')
        worksheet = workbook.add_worksheet('Change Report')

        # write header to first row
        cell_format = workbook.add_format({'bold': True, 'font_color': 'black'})
        worksheet.write(0, 0, 'Device', cell_format)
        worksheet.write(0, 1, 'Promo Location', cell_format)
        worksheet.write(0, 2, 'Promo Text', cell_format)
        worksheet.write(0, 3, 'Promo URL', cell_format)

        # start from second row
        row = 1

        # add promos
        for promo in scraped_promos_today_plus_discontinued:
            if promo in removed:
                cell_format = workbook.add_format({'bold': True, 'font_color': 'purple'})
            elif promo in added:
                cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})
            else:
                cell_format = workbook.add_format({'bold': False, 'font_color': 'black'})
            worksheet.write(row, 0, promo.device_name + ' (' + str(promo.device_storage) + ')', cell_format)
            worksheet.write(row, 1, promo.promo_location, cell_format)
            worksheet.write(row, 2, promo.promo_text, cell_format)
            worksheet.write(row, 3, promo.url, cell_format)
            row += 1

        workbook.close()

    print('Change Reports Generated')

changes_report(today, yesterday)



