
class ScrapedPrepaidPrice:

    def __init__(self, provider='N/A', device='N/A', storage='N/A', list_price='0.00',
                 retail_price='0.00', url='N/A', date='N/A', time='N/A'):
        self.provider = provider
        self.device = device.strip()
        self.storage = storage
        self.list_price = list_price
        self.retail_price = retail_price
        self.url = url
        self.date = date
        self.time = time

    def validate_prepaid(self, provider, device, storage, list_price, retail_price, url, date, time):
        if provider not in ['verizon', 'att', 'cricket', 'metropcs']:
            print('Invalid provider')
            return False
        if device == 'N/A':
            print('Device missing')
            return False
        if not isinstance(storage, int):
            print('Invalid storage')
            return False
        if not list_price.isdigit():
            print('Invalid list price')
            return False
        if not retail_price.isdigit():
            print('Invalid retail price')
            return False
        if url == 'N/A':
            print('Invalid url')
            return False
        if date == 'N/A':
            print('Invalid date')
            return False
        if time == 'N/A':
            print('Invalid time')
            return False
        return True
