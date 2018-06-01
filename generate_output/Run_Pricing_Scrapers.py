# from scrapers.pricing.Att_Pricing_Prepaid import att_scrape_prepaid_smartphone_prices
# from scrapers.pricing.Cricket_Pricing_Prepaid import cri_scrape_prepaid_smartphone_prices
# from scrapers.pricing.Metropcs_Pricing_Prepaid import met_scrape_prepaid_smartphone_prices
# from scrapers.pricing.Verizon_Pricing_Prepaid import ver_scrape_prepaid_smartphone_prices
# from scrapers.pricing.Att_Pricing_Postpaid import att_scrape_postpaid_smartphone_prices
from scrapers.pricing.Att_Pricing_Postpaid_Tablets import att_scrape_postpaid_tablet_prices
# from scrapers.pricing.Sprint_Pricing_Postpaid import spr_scrape_postpaid_smartphone_prices
# from scrapers.pricing.Sprint_Pricing_Postpaid_Tablets import spr_scrape_postpaid_tablet_prices
# from scrapers.pricing.Tmobile_Pricing_Postpaid import tmo_scrape_postpaid_smartphone_prices
# from scrapers.pricing.Tmobile_Pricing_Postpaid_Tablets import tmo_scrape_postpaid_tablet_prices
from scrapers.pricing.Verizon_Pricing_Postpaid import ver_scrape_postpaid_smartphone_prices
from scrapers.pricing.Verizon_Pricing_Postpaid_Tablets import ver_scrape_postpaid_tablet_prices
import datetime
from data.model.Price import get_day_before
# from scrapers.promotions.Compare_Today_To_Yesterday_Promotions import generate_changes_report

today = datetime.datetime.now().date()
yesterday = get_day_before(today)

# print(datetime.datetime.now().time())
# cri_scrape_prepaid_smartphone_prices()
# print('-> Cricket Prepaid Smartphones Complete')
# generate_changes_report('cricket', today, yesterday)
# print(datetime.datetime.now().time())
# tmo_scrape_postpaid_smartphone_prices()
# print('-> T-Mobile Postpaid Smartphones Complete')
# print(datetime.datetime.now().time())
# tmo_scrape_postpaid_tablet_prices()
# print('-> T-Mobile Postpaid Tablets Complete')
# print(datetime.datetime.now().time())
# spr_scrape_postpaid_smartphone_prices()
# print('-> Sprint Postpaid Smartphones Complete')
# print(datetime.datetime.now().time())
# spr_scrape_postpaid_tablet_prices()
# print('-> Sprint Postpaid Tablets Complete')
# print(datetime.datetime.now().time())
# met_scrape_prepaid_smartphone_prices()
# print('-> MetroPCS Prepaid Smartphones Complete')
# print(datetime.datetime.now().time())
# att_scrape_postpaid_smartphone_prices()
# print('-> AT&T Postpaid Smartphones Complete')
print(datetime.datetime.now().time())
att_scrape_postpaid_tablet_prices()
print('-> AT&T Postpaid Tablets Complete')
# print(datetime.datetime.now().time())
# att_scrape_prepaid_smartphone_prices()
# print('-> AT&T Prepaid Smartphones Complete')
# print(datetime.datetime.now().time())
ver_scrape_postpaid_smartphone_prices()
print('-> Verizon Postpaid Smartphones Complete')
print(datetime.datetime.now().time())
ver_scrape_postpaid_tablet_prices()
print('-> Verizon Postpaid Tablets Complete')
print(datetime.datetime.now().time())
# ver_scrape_prepaid_smartphone_prices()
# print('-> Verizon Prepaid Smartphones Complete')
# print(datetime.datetime.now().time())