import datetime

today = datetime.date.today()
day_of_week = datetime.timedelta(today.weekday())
sub_end_date = today - day_of_week + datetime.timedelta(days=13)
sub_end_date_flagship = today - (day_of_week - datetime.timedelta(days=4)) + datetime.timedelta(days=13)

class Calendar_deal:

    def __init__(self, provider, category, deal_id, devices, promotion_details, promotion_summary, url, status,
                 modified_summary, date, homepage, start_date):
        self.provider = provider
        self.category = category
        self.deal_id = deal_id
        devices = devices.lower()
        devices = devices.split(',')
        devices = [device.lstrip() for device in devices]
        self.devices = devices
        flagship = 0
        iconic = 0
        for device in devices:
            if device == 'galaxy s9' or device == 'galaxy s9+' or device == 'galaxy 8' or device == 'galaxy 8+' \
                    or device == 'galaxy s8' or device == 'galaxy s8+'or device == 'galaxy s8 active' or device == 'galaxy note8':
                iconic, flagship = 1, 1
                continue
            if device == 'galaxy s9' or device == 'galaxy s9+' or device == 'iphone x' or device == 'iphone 8' or \
                            device == 'iphone 8 plus' or device == 'galaxy 8' or device == 'galaxy 8+' or device == 'galaxy s8 active' or \
                            device == 'galaxy note8' or device == 'lg g6' or device == 'lg v30' or device == 'lg v30+' or \
                            device == 'moto z2 force edition' or device == 'android*' or device == 'pixel 2' \
                            or device == 'pixel 2 xl' or device == 'iphone*' or device == 'galaxy*' or device == 'iphone x':
                flagship = 1
                continue
        if flagship == 0:
            self.flagship = 'no'
        elif flagship == 1:
            self.flagship = 'yes'
        if iconic == 0:
            self.iconic = 'no'
        elif iconic == 1:
            self.iconic = 'yes'
        self.promotion_details = promotion_details
        if 'smart speaker' in promotion_summary:
            self.budget = 'no'
        elif category != 'smartphone other':
            self.budget = 'no'
        elif '$5.00/mo' in promotion_summary or '$5/mo' in promotion_summary or '$5 mo' in promotion_summary or \
                        'free' in promotion_summary or 'Free' in promotion_summary or '$0/mo' in promotion_summary\
                        or ' $0.00/mo' in promotion_summary or '$0 mo' in promotion_summary or '$4/mo' in promotion_summary\
                        or '$4 mo' in promotion_summary or '$3/mo' in promotion_summary or '$3 mo' in promotion_summary:
            self.budget = 'yes'
        else:
            self.budget = 'no'
        self.promotion_summary = promotion_summary
        self.url = url
        self.status = status
        self.modified_summary = modified_summary
        self.date = date
        self.homepage = homepage
        self.start_date_ref = start_date
        self.start_date = start_date.strftime('%#m/%d')
        self.start_date_cal = start_date.strftime('%Y-%m-%d')
        if self.status == 'discontinued':
            self.end_date = date.strftime('%#m/%d')
            self.end_date_ref = date
            self.end_date_ref_flagship = date
            self.end_date_cal = date.strftime('%Y-%m-%d')
        else:
            self.end_date = "..."
            self.end_date_ref = sub_end_date
            self.end_date_ref_flagship = sub_end_date_flagship
            self.end_date_cal = sub_end_date.strftime('%Y-%m-%d')