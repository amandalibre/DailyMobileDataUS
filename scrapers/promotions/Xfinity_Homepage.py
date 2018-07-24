# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion
import json
import requests


def xfi_scrape_homepage():
    # make object
    scraped_promotion = ScrapedPromotion()

    # hardcoded variables
    scraped_promotion.provider = 'xfinity'
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()
    scraped_promotion.promo_location = 'homepage'
    scraped_promotion.device_storage = '0'
    scraped_promotion.url = "https://www.xfinity.com/mobile/"

    # scrape json
    device_page = requests.get('https://cdn.comcast.com/mobile-static/content/20180720-2015/variants/default/pages/landing.json')
    device_soup = BeautifulSoup(device_page.text, 'html.parser')
    device_json = json.loads(device_soup.text)

    # carousel
    for actions in device_json["carousel"]["default"]:
        scraped_promotion.promo_text = actions["actions"]["popovers"][0]["data"]["body"]
        print(scraped_promotion.provider, scraped_promotion.device_name,  scraped_promotion.device_storage,
              scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
              scraped_promotion.date, scraped_promotion.time)
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)

    # plan info
    for item in device_json["contentItems"]:
        try:
            scraped_promotion.promo_text = item["content"]["description"]
            print(scraped_promotion.provider, scraped_promotion.device_name,  scraped_promotion.device_storage,
                  scraped_promotion.promo_location, scraped_promotion.promo_text, scraped_promotion.url,
                  scraped_promotion.date, scraped_promotion.time)
            add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                               scraped_promotion.device_storage, scraped_promotion.promo_location,
                                               scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                               scraped_promotion.time)
        except KeyError:
            pass







