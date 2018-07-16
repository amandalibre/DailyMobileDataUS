# -*- coding: utf-8 -*-
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion


def xfi_scrape_prepaid_promotins(url, device_name, device_storage, description):
    # make object
    scraped_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_promotion.provider = 'xfinity'
    scraped_promotion.device_name = device_name
    scraped_promotion.device_storage = device_storage
    scraped_promotion.url = url
    scraped_promotion.promo_text = description
    scraped_promotion.promo_location = 'description'

    # time variables
    scraped_promotion.date = datetime.date.today()
    scraped_promotion.time = datetime.datetime.now().time()

    # add to database
    add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                       scraped_promotion.device_storage, scraped_promotion.promo_location,
                                       scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                       scraped_promotion.time)