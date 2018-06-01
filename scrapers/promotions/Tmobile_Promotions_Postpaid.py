# -*- coding: utf-8 -*-
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from selenium.common.exceptions import NoSuchElementException
from data.model.Scraped_Promotion import ScrapedPromotion

def tmo_scrape_postpaid_promotions(driver, soup, url, device_name, device_storage):
    # make object
    scraped_postpaid_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_postpaid_promotion.provider = 'tmobile'
    scraped_postpaid_promotion.device_name = device_name
    scraped_postpaid_promotion.device_storage = device_storage
    scraped_postpaid_promotion.url = url

    # make empty list of promotions
    promotions = []

    # upper banner text
    try:
        upper_banner_text = driver.find_element_by_id('promo-banner')
        promotions.append(['upper banner', upper_banner_text.text])
    except NoSuchElementException:
        print('no upper banner text')

    # banner under device name text
    for div2 in soup.findAll("div", class_="text-magenta ng-scope"):
        promotions.append(['banner under device name', div2.text])

    # crossed out text (if savings is anything other than $0.00)
    strike_out_price = soup.findAll('span', class_='text-magenta ng-binding')
    if strike_out_price[0].text != '($0.00 Savings)':
        promotions.append(['discount', strike_out_price[0].text])

    # make object for each promo text instance
    for promo_instance in promotions:
        scraped_postpaid_promotion.promo_location = promo_instance[0]
        scraped_postpaid_promotion.promo_text = promo_instance[1]

        # time variables
        scraped_postpaid_promotion.date = datetime.date.today()
        scraped_postpaid_promotion.time = datetime.datetime.now().time()

        # add to database
        add_scraped_promotions_to_database(scraped_postpaid_promotion.provider, scraped_postpaid_promotion.device_name,
                                           scraped_postpaid_promotion.device_storage, scraped_postpaid_promotion.promo_location,
                                           scraped_postpaid_promotion.promo_text, scraped_postpaid_promotion.url,
                                           scraped_postpaid_promotion.date, scraped_postpaid_promotion.time)