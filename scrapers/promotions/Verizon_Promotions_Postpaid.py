# -*- coding: utf-8 -*-
import datetime
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
from data.database.Database_Methods import add_scraped_promotions_to_database
from data.model.Scraped_Promotion import ScrapedPromotion


def ver_scrape_postpaid_promotions(soup, driver, url, device_name, device_storage):
    # make object
    scraped_promotion = ScrapedPromotion()

    # set variables already determined
    scraped_promotion.provider = 'verizon'
    scraped_promotion.device_name = device_name
    scraped_promotion.device_storage = device_storage
    scraped_promotion.url = url

    # make empty list of promotions
    promotions = []

    # alternate way to get banner text
    upper_banner_text_2 = driver.find_element_by_class_name('clearfix')
    if upper_banner_text_2.text.strip() != '':
        promotions.append(['upper banner', upper_banner_text_2.text.strip()])

    # crossed out price
    pricing_options = soup.findAll('div', class_='pad8 noRightPad')
    for div in pricing_options:
        if 'was' in div.text:
            promotions.append(['crossed out price', div.text.replace('2-Year Contract', ' 2-Year Contract').replace('24 Monthly Payments',' 24 Monthly Payments').replace('was ', ' was')])

    # each payment option has its own banners
    for option in range(1, len(pricing_options) + 1):
        option_button = driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[3]/div[1]/div/div[2]/div/div/div[1]/div/div[' + str(option) + ']/div/div/div')

        # PAYMENT LEVEL
        # click on different payment options to show different promos
        # if popup is there, remove it before clicking
        try:
            option_button.click()
        except WebDriverException:
            driver.find_element_by_class_name('fsrCloseBtn').click()
            print('popup clicked')
            option_button.click()
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # promotion text above device icon
        try:
            banner_above_icon = soup.find('div', class_='offersPad fontSize_12 lineHeight8')
            promotions.append(['banner above device icon', banner_above_icon.text.replace('Special Offer', '').replace('See the details', '').replace('\n', '')])
        except AttributeError:
            print('no banner above device icon')

        # banner under price
        below_price_banner = soup.find('div', class_='row padTop6 noSideMargin priceLabel').text
        if below_price_banner != 'Retail Price' and below_price_banner != 'Early Termination Fee: $175 (2-Year Contracts)':
            promotions.append(['banner below price', below_price_banner])

    # make object for each promo text instance
    for promo_instance in promotions:
        scraped_promotion.promo_location = promo_instance[0]
        scraped_promotion.promo_text = promo_instance[1]

        # hardcoded variables
        scraped_promotion.date = datetime.date.today()
        scraped_promotion.time = datetime.datetime.now().time()

        print(scraped_promotion.provider, scraped_promotion.device_name,
                                           scraped_promotion.device_storage, scraped_promotion.promo_location,
                                           scraped_promotion.promo_text, scraped_promotion.url,
                                           scraped_promotion.date, scraped_promotion.time)

        # # add to database
        # add_scraped_promotions_to_database(scraped_promotion.provider, scraped_promotion.device_name,
        #                                    scraped_promotion.device_storage, scraped_promotion.promo_location,
        #                                    scraped_promotion.promo_text, scraped_promotion.url,
        #                                    scraped_promotion.date, scraped_promotion.time)





