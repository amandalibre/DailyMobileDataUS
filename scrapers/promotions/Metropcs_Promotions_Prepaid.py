# -*- coding: utf-8 -*-
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion


def met_scrape_prepaid_promotins(soup, url, device_name, device_storage):
    # make object
    scraped_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_promotion.provider = 'metropcs'
    scraped_promotion.device_name = device_name
    scraped_promotion.device_storage = device_storage
    scraped_promotion.url = url

    # make empty list of promotions
    promotions = []

    # crossed out price
    try:
        crossed_out_price = soup.find('span', class_='normal-price')
        promotions.append(['crossed out price',
                           crossed_out_price.text.strip().replace('\n', '').replace('                                ',
                                                                                    '.')])
    except AttributeError:
        crossed_out_price = ''

    # make object for each promo text instance
    for promo_instance in promotions:
        scraped_promotion.promo_location = promo_instance[0]
        scraped_promotion.promo_text = promo_instance[1]

        # time variables
        scraped_promotion.date = datetime.date.today()
        scraped_promotion.time = datetime.datetime.now().time()

        # add to database
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)