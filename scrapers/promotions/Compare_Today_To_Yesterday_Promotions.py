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

        # create list of what was removed today
        set1 = set((promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) for promo in scraped_promotions_today)
        removed = [promo for promo in scraped_promotions_yesterday if (promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) not in set1]

        # create list of what was added today
        set2 = set((promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) for promo in scraped_promotions_yesterday)
        added = [promo for promo in scraped_promotions_today if (promo.device_name, promo.device_storage, promo.promo_location, promo.promo_text) not in set2]

        # combine today's promotions with those removed today
        scraped_promos_today_plus_discontinued = scraped_promotions_today + removed
        scraped_promos_today_plus_discontinued.sort(key=lambda promo: promo.device_name, reverse=True)

        # Create an Excel workbook and add worksheet
        workbook = xlsxwriter.Workbook(r'C:\Users\Amanda Friedman\PycharmProjects\DailyPromotionsAndPricing\Promo Change Report\_' + provider.title() + '_Promo_Change_Report_' + str(today) +'.xlxs')
        worksheet = workbook.add_worksheet('By Device')

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

        # create empty list of promo_text_today for all promos (removed, added or unchanged)
        promo_text_today = []

        # create consolidated list of all promos (removed, added or unchanged)
        for promo in scraped_promos_today_plus_discontinued:
            if promo.promo_text not in promo_text_today:
                promo_text_today.append(promo.promo_text)

        # make copy of promo_text_today list (so that copy has same amount of entries to append to in next step)
        promo_view_today = promo_text_today

        # make list of lists of promotions
        for promo_text_row in range(len(promo_text_today)):

            # edit row of promo_view_today to be list of lists
            promo_view_today[promo_text_row] = [promo_text_today[promo_text_row], [], [], []]

            # find promos with the same promo.text as first entry in list
            for promo in scraped_promos_today_plus_discontinued:
                if promo.promo_text == promo_text_today[promo_text_row][0]:

                    # if promo is removed, add device name (size) to removed column
                    if promo in removed:
                        promo_view_today[promo_text_row][3].append(promo.device_name + ' (' + str(promo.device_storage) + ')')

                    # if promo is added, add deice name (size) to device list column and added column
                    elif promo in added:
                        promo_view_today[promo_text_row][2].append(promo.device_name + ' (' + str(promo.device_storage) + ')')
                        promo_view_today[promo_text_row][1].append(promo.device_name + ' (' + str(promo.device_storage) + ')')

                    # if promo is unchanged, add device name (size) to device list column
                    else:
                        promo_view_today[promo_text_row][1].append(promo.device_name + ' (' + str(promo.device_storage) + ')')

        # create second worksheet
        worksheet2 = workbook.add_worksheet('By Promo')

        # write header to first row
        cell_format = workbook.add_format({'bold': True, 'font_color': 'black'})
        worksheet2.write(0, 0, 'Promo', cell_format)
        worksheet2.write(0, 1, 'Devices List', cell_format)
        worksheet2.write(0, 2, 'Devices Added', cell_format)
        worksheet2.write(0, 3, 'Devices Removed', cell_format)

        # start from second row
        row = 1

        # add promos
        for promo_text_row in promo_view_today:
            if promo_text_row[3]:
                cell_format = workbook.add_format({'bold': True, 'font_color': 'purple'})
            elif promo_text_row[2]:
                cell_format = workbook.add_format({'bold': True, 'font_color': 'red'})
            else:
                cell_format = workbook.add_format({'bold': False, 'font_color': 'black'})
            worksheet2.write(row, 0, promo_text_row[0], cell_format)
            worksheet2.write(row, 1, str(promo_text_row[1]), cell_format)
            worksheet2.write(row, 2, str(promo_text_row[2]), cell_format)
            worksheet2.write(row, 3, str(promo_text_row[3]), cell_format)
            row += 1

        workbook.close()

    print('Change Reports Generated')


changes_report(today, yesterday)



