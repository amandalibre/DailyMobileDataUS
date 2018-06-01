# -*- coding: utf-8 -*-
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion


def att_scrape_postpaid_promotions(soup, url, device_name, device_storage):
    # make object
    scraped_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_promotion.provider = 'att'
    scraped_promotion.device_name = device_name
    scraped_promotion.device_storage = device_storage
    scraped_promotion.url = url

    # make empty list of promotions
    promotions = []

    # upper banner text
    for span in soup.findAll("span", class_="offerTxt"):
        if span.text.strip() != '':
            upper_banner_text = span.text.strip()
            promotions.append(['upper banner', upper_banner_text])

    # lower banner text
    for div in soup.findAll("div", class_="ds2MarketingMessageTextStyle"):
        promotions.append(['lower banner', div.text])

    # make object for each promo text instance
    for promo_instance in promotions:
        scraped_promotion.promo_location = promo_instance[0]
        scraped_promotion.promo_text = promo_instance[1]

        # hardcoded variables
        scraped_promotion.date = datetime.date.today()
        scraped_promotion.time = datetime.datetime.now().time()

        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url, scraped_promotion.date,
                                           scraped_promotion.time)



