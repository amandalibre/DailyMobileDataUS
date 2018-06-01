class ScrapedPromotion():

    def __init__(self, url='N/A', device_name='N/A', device_storage='N/A', promo_location='N/A', promo_text='N/A', provider='N/A', date='N/A', time='N/A'):
        self.url = url
        self.device_name = device_name.lower()
        self.device_storage = device_storage
        self.promo_location = promo_location
        self.promo_text = promo_text
        self.provider = provider
        self.date = date
        self.time = time

