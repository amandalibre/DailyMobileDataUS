import datetime
from bs4 import BeautifulSoup
from data.database.Database_Methods import add_iphone_shipment_to_database
import json
import requests

url_list = [['https://www.apple.com/shop/retail/pickup-message?parts.0=MT952LL%2FA&parts.1=MT982LL%2FA&parts.2=MT9C2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT952LL%2FA&parts.1=MT982LL%2FA&parts.2=MT9C2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537211893979'],
            ['https://www.apple.com/shop/retail/pickup-message?parts.0=MT942LL%2FA&parts.1=MT972LL%2FA&parts.2=MT9A2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT942LL%2FA&parts.1=MT972LL%2FA&parts.2=MT9A2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537213207385'],
            ['https://www.apple.com/shop/retail/pickup-message?parts.0=MT962LL%2FA&parts.1=MT992LL%2FA&parts.2=MT9D2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT962LL%2FA&parts.1=MT992LL%2FA&parts.2=MT9D2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537213207386'],
            ['https://www.apple.com/shop/retail/pickup-message?parts.0=MT5A2LL%2FA&parts.1=MT5E2LL%2FA&parts.2=MT5H2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT5A2LL%2FA&parts.1=MT5E2LL%2FA&parts.2=MT5H2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537213207387'],
            ['https://www.apple.com/shop/retail/pickup-message?parts.0=MT592LL%2FA&parts.1=MT5D2LL%2FA&parts.2=MT5G2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT592LL%2FA&parts.1=MT5D2LL%2FA&parts.2=MT5G2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537213207388'],
            ['https://www.apple.com/shop/retail/pickup-message?parts.0=MT5C2LL%2FA&parts.1=MT5F2LL%2FA&parts.2=MT5J2LL%2FA&little=true&cppart=UNLOCKED%2FUS&store=R250',
             'https://www.apple.com/shop/delivery-message?parts.0=MT5C2LL%2FA&parts.1=MT5F2LL%2FA&parts.2=MT5J2LL%2FA&little=true&cppart=UNLOCKED%2FUS&_=1537213207389'],
            ]

for url_pair in url_list:

    # get basePartNumbers
    base_part_num_dict = {}
    device_page = requests.get(url_pair[0])
    device_soup = BeautifulSoup(device_page.text, 'html.parser')
    device_json = json.loads(device_soup.text)
    for device in device_json["body"]["stores"][0]["partsAvailability"]:
        base_part_num_dict.update({device: device_json["body"]["stores"][0]["partsAvailability"][device]["storePickupProductTitle"]})

    # get deliver dates
    device_page = requests.get(url_pair[1])
    delivery_soup = BeautifulSoup(device_page.text, 'html.parser')
    delivery_json = json.loads(delivery_soup.text)
    for key, value in base_part_num_dict.items():
        print(value, delivery_json["body"]["content"]["deliveryMessage"][key]["label"], delivery_json["body"]["content"]["deliveryMessage"][key]["quote"])