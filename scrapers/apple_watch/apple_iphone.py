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
    headers = {'Cookie': "s_fid=0BD367D04A1AAEF5-1188FD3E4CC35D59; s_vi=[CS]v1|2D2137ED052C9BD8-400009DE80004266[CE]; dssid2=7c29b673-b68d-4f2e-bb46-07222e84f7ef; dssf=1; as_sfa=Mnx1c3x1c3x8ZW5fVVN8Y29uc3VtZXJ8aW50ZXJuZXR8MHwwfDE=; optimizelyEndUserId=oeu1514303464607r0.49015980240875856; pxro=1; as_loc=b8fd8ebaa92ce2ad09485fca20e43c0c6b770b6f6ad5bc2d504c053c46f14e39c564a333399cc785ff87db07d748d06307114f723002d760e1958b425522209935ceaf462e4e4a52ffe600a809a00a464f3c7558f12fc6ef1050575abbc4de15; s_vnum_n2_us=3%7C2%2C0%7C2%2C12%7C1%2C13%7C1; xp_ci=3zxq0nxzDnZz5OLz9qlz15IygaOVn; optimizelySegments=%7B%22341793217%22%3A%22search%22%2C%22341794206%22%3A%22false%22%2C%22341824156%22%3A%22gc%22%2C%22341932127%22%3A%22none%22%7D; optimizelyBuckets=%7B%2211110986997%22%3A%2211101508001%22%7D; s_cc=true; rtsid=%7BUS%3D%7Bt%3Da%3Bi%3DR250%3B%7D%3B%7D; as_pcts=e8PJ9Jv6uCr6+Zg4Qj8Bahojxi3uEJgJR1uR2KJNCSpklvuclt2MzvOe+4Om8; as_dc_pod=rno_88-0; s_ptc=0.003%5E%5E0.000%5E%5E0.000%5E%5E0.000%5E%5E0.124%5E%5E0.005%5E%5E1.211%5E%5E0.017%5E%5E0.176%5E%5E1.411%5E%5E0.001%5E%5E1.555; s_sq=appleusiphonexs%252Capplestoreww%3D%2526c.%2526a.%2526activitymap.%2526page%253Diphone%252520xs%252520-%252520index%252520%252528us%252529%2526link%253DPre-order%252520-%252520%25252Fus%25252Fshop%25252Fgoto%25252Fbuy_iphone%25252Fiphone_xs%252520-%252520ac-localnav%2526region%253Dac-localnav%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Diphone%252520xs%252520-%252520index%252520%252528us%252529%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.apple.com%25252Fus%25252Fshop%25252Fgoto%25252Fbuy_iphone%25252Fiphone_xs%2526ot%253DA; as_atb=1.0|MjAxOC0wOS0xNyAwMjowNzo0OQ|44912b7e7a74f07b992cf4610cb0b9daa952693b; as_dc=nwk"}
    device_page = requests.get(url_pair[1], headers=headers)
    delivery_soup = BeautifulSoup(device_page.text, 'html.parser')
    delivery_json = json.loads(delivery_soup.text)
    for key, value in base_part_num_dict.items():
        print(value, delivery_json["body"]["content"]["deliveryMessage"][key]["label"], delivery_json["body"]["content"]["deliveryMessage"][key]["quote"])