class ScrapedDevice:

    def __init__(self, provider='N/A', device='N/A', storage='N/A', url='N/A', config_url='N/A', date='N/A', time='N/A'):
        self.provider = provider
        self.device = device.strip()
        self.storage = storage
        self.url = url
        self.config_url = config_url
        self.date = date
        self.time = time


class ScrapedPostpaidPrice(ScrapedDevice):

    def __init__(self, provider, device, storage, url, config_url, date, time,
                 monthly_price='0.00', onetime_price='0.00', retail_price='0.00', contract_ufc='0.00', ):
        ScrapedDevice.__init__(self, provider, device, storage, url, config_url, date, time)
        self.monthly_price = monthly_price
        self.onetime_price = onetime_price
        self.retail_price = retail_price
        self.contract_ufc = contract_ufc


class ScrapedPrepaidPrice(ScrapedDevice):

    def __init__(self, provider, device, storage, url, config_url, date, time,
                 list_price='0.00', retail_price='0.00'):
        ScrapedDevice.__init__(self, provider, device, storage, url, config_url, date, time)
        self.list_price = list_price
        self.retail_price = retail_price


class ScrapedPromotion(ScrapedDevice):

    def __init__(self, provider, device, storage, url, config_url, date, time,
                 promo_location='N/A', promo_text='N/A'):
        ScrapedDevice.__init__(self, provider, device, storage, url, config_url, date, time)
        self.promo_location = promo_location
        self.promo_text = promo_text
