
class ScrapedPostpaidPrice():

    def __init__(self, provider='N/A', device='N/A', storage='N/A', monthly_price='0.00', onetime_price='0.00',
                 retail_price='0.00', contract_ufc='0.00', url='N/A', config_url='N/A', date='N/A', time='N/A'):
        self.provider = provider
        self.device = device.strip()
        self.storage = storage
        self.monthly_price = monthly_price
        self.onetime_price = onetime_price
        self.retail_price = retail_price
        self.contract_ufc = contract_ufc
        self.url = url
        self.config_url = config_url
        self.date = date
        self.time = time

    def validate_postpaid(self, provider, device, storage, monthly_price, onetime_price, retail_price, contract_ufc,
                          url, config_url, date, time):
        if provider not in ['verizon', 'att', 'tmobile', 'sprint']:
            print('Invalid provider')
            return False
        if device == 'N/A':
            print('Device missing')
            return False
        if not isinstance(storage, int):
            print('Invalid storage')
            return False
        if not monthly_price.isdigit():
            print('Invalid monthly price')
            return False
        if not onetime_price.isdigit():
            print('Invalid onetime price')
            return False
        if not retail_price.isdigit():
            print('Invalid retail price')
            return False
        if not contract_ufc.isdigit():
            print('Invalid contract ufc price')
            return False
        if url == 'N/A':
            print('Invalid url')
            return False
        if provider == 'att':
            if config_url == 'N/A':
                print('Invalid config_url')
                return False
        if date == 'N/A':
            print('Invalid date')
            return False
        if time == 'N/A':
            print('Invalid time')
            return False
        return True
