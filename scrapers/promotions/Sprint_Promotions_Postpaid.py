# -*- coding: utf-8 -*-
import datetime
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion
from selenium.common.exceptions import NoSuchElementException


def spr_scrape_postpaid_promotions(soup, url, device_name, device_storage):
    # make object
    scraped_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_promotion.provider = 'sprint'
    scraped_promotion.device_name = device_name
    scraped_promotion.device_storage = device_storage
    scraped_promotion.url = url

    # make empty list of promotions
    promotions = []

    # # upper banner text (not all pages have banners)
    # try:
    #     upper_banner_text = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div/div/div/div/div')
    #     promotions.append(['upper banner', upper_banner_text.text.strip()])
    # except NoSuchElementException:
    #     print('no upper banner')

    # promotion text under price box
    price_boxes = soup.findAll('div', class_='col-xs-24 col-lg-24 col-xl-24 mb-20 active')
    for box in price_boxes:
        if box.find('strong', class_='display-block font-size-16 font-size-md-18 color--blue').text != ' Full price':
            for li in box.findAll('li', class_='promo-item'):
                promotions.append(['banner under Sprint Flex box', li.text.replace('Detail', '').strip()])

    # crossed out price
    strike_out_price = soup.findAll('del', class_='sprint-price-del')
    if strike_out_price[0].text != '':
        promotions.append(['crossed out price', strike_out_price[0].text])

    # make object for each promo text instance
    for promo_instance in promotions:
        scraped_promotion.promo_location = promo_instance[0]
        scraped_promotion.promo_text = promo_instance[1]

        # time variables
        scraped_promotion.date = datetime.date.today()
        scraped_promotion.time = datetime.datetime.now().time()

        # add to database
        add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage,
                                           scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url,
                                           scraped_promotion.date, scraped_promotion.time)