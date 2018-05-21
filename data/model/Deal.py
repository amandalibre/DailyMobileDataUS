class Deal:

    def __init__(self, provider, category, deal_id, devices, promotion_details, promotion_summary, url, status,
                 modified_summary, date, homepage, filename_provider, filename_date):
        self.provider = provider.strip().lower()
        self.category = category.strip().lower()
        self.deal_id = deal_id
        self.devices = devices
        self.promotion_details = promotion_details
        self.promotion_summary = promotion_summary
        self.url = url
        self.status = status.strip().lower()
        self.modified_summary = modified_summary
        self.date = date
        self.date_mysql = date[-4:] + date[-5] + date[0:-5]
        self.homepage = homepage.strip().lower()
        self.filename_provider = filename_provider
        self.filename_date = filename_date
        self.start_date = self.deal_id[8:10] + "-" + self.deal_id[6:8] + "-" + self.deal_id[2:6]
        self.start_date_mysql = self.deal_id[2:6] + "-" + self.deal_id[6:8] + "-" + self.deal_id[8:10]



