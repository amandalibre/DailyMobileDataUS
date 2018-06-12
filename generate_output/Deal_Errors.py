from datetime import datetime
import itertools

provider_names = ['verizon', 'att', 'tmobile', 'sprint', 'xfinity', 'metropcs', 'cricket']


def deals_errors(deals_by_provider, approved_device_list):
    errors = 0
    for i in range(6):
        # check if promotion_details is duplicated on CSV
        for a, b in itertools.combinations(deals_by_provider[provider_names[i]], 2):
            if a.promotion_details == b.promotion_details:
                print(provider_names[i] + " file: duplicate promo language '" + a.promotion_details + "'")
                errors += 1
            if a.deal_id == b.deal_id:
                print(provider_names[i] + " file: duplicate deal_id '" + a.deal_id + "'")
                errors += 1
        for deal in deals_by_provider[provider_names[i]]:
            # check for incorrect provider
            if deal.provider != "verizon" and deal.provider != "att" and deal.provider != "tmobile" and \
                    deal.provider != "sprint" and deal.provider != "metropcs" and deal.provider != "cricket"\
                    and deal.provider != 'xfinity':
                print(provider_names[i] + " file: incorrect provider '" + deal.provider + "' in deal '" + deal.promotion_details + "'")
                errors += 1
            # check for incorrect category
            if deal.category != "bogo" and deal.category != "smartphone other" and deal.category != "tablet" and deal.category != "data plan/network" and deal.category != "trade-in" and deal.category != "switcher":
                print(provider_names[i] + " file: incorrect category '" + deal.category + "' in deal '" + deal.promotion_details + "'")
                errors += 1
            # check for incorrect status
            if deal.status != "no change" and deal.status != "modified" and deal.status != "discontinued" and deal.status != "new":
                print(provider_names[i] + " file: incorrect status '" + deal.status + "' in deal '" + deal.promotion_details + "'")
                errors += 1
            # check for modified offer without modified_summary
            if deal.status == "modified" and deal.modified_summary == "":
                print(provider_names[i] + " file: modified offer missing modified_summary in deal '" + deal.promotion_details + "'")
                errors += 1
            # check for devices
            if deal.category != "data plan/network" and deal.devices == "":
                print(provider_names[i] + " file: no devices specified in deal '" + deal.promotion_details + "'")
                errors += 1
            if deal.category != 'data plan/network':
                wrong_devices = []
                device_list = deal.devices.lower()
                device_list = device_list.split(',')
                for device in device_list:
                    if device.strip() not in approved_device_list:
                        wrong_devices.append(device.strip())
                if wrong_devices:
                    print(provider_names[i] + " file: devices " + str(wrong_devices) + " not recognized in deal '" + deal.promotion_details + "'")
                    errors += 1
            # check for errors in new deal_id number
            if deal.status == "new":
                if deal.deal_id[0] != deal.provider[0].upper():
                    print(provider_names[i] + " file: first letter in new deal_id doesn't match provider name in deal '" + deal.promotion_details + "'")
                    errors += 1
                if datetime.strptime(deal.date, '%m/%d/%Y').strftime('%Y%m%d') != deal.deal_id[2:10]:
                    print(provider_names[i] + " file: date in new deal_id '" + deal.deal_id + "' doesn't match today's date in deal " + deal.promotion_details + "'")
                    errors += 1
            # check for errors in non-new deal_id
            if len(deal.deal_id) != 13:
                print(provider_names[i] + " file: deal_id '" + deal.deal_id + "' should have 13 characters X-YYYYMMDD-## in deal '" + deal.promotion_details + "'")
                errors += 1
            if datetime.today() < datetime.strptime((deal.deal_id[2:10]), '%Y%m%d'):
                print(provider_names[i] + " file: date in deal_id " + deal.deal_id + " is in the future in deal " + deal.promotion_details + "'")
                errors += 1
            # check that provider in filename and column 1 match
            if deal.filename_provider != deal.provider:
                print(provider_names[i] + " file: provider name in file title '" + deal.provider + "' does not match provider name in CSV in deal '" + deal.promotion_details + "'")
                errors += 1
            # check that the date in filename and date in column 10 match
            if deal.filename_date != datetime.strptime(deal.date_mysql, '%Y/%m/%d').strftime('%Y-%m-%d'):
                print(provider_names[i] + " file: date '" + deal.date + "' does not match date in file title in deal '" + deal.promotion_details + "'")
                errors += 1
            # check that homepage has either "yes" or "no"
            if deal.homepage != "yes" and deal.homepage != "no":
                print(provider_names[i] + " file: homepage should be 'yes' or 'no' but is '" + deal.homepage + "' in '" + deal.promotion_details + "'")
                errors += 1
    print("Found " + str(errors) + " errors in CSV files.")
    if errors > 0:
        print("Process stopped. Fix the errors!")
        exit()