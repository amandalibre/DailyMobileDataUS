from scrapers.pricing.Att_Pricing_Prepaid import att_scrape_prepaid_smartphone_prices
from scrapers.pricing.Cricket_Pricing_Prepaid import cri_scrape_prepaid_smartphone_prices
from scrapers.pricing.Metropcs_Pricing_Prepaid import met_scrape_prepaid_smartphone_prices
from scrapers.pricing.Verizon_Pricing_Prepaid import ver_scrape_prepaid_smartphone_prices
from scrapers.pricing.Att_Pricing_Postpaid import att_scrape_postpaid_smartphone_prices
from scrapers.pricing.Att_Pricing_Postpaid_Tablets import att_scrape_postpaid_tablet_prices
from scrapers.pricing.Sprint_Pricing_Postpaid import spr_scrape_postpaid_smartphone_prices
from scrapers.pricing.Sprint_Pricing_Postpaid_Tablets import spr_scrape_postpaid_tablet_prices
from scrapers.pricing.Tmobile_Pricing_Postpaid import tmo_scrape_postpaid_smartphone_prices
from scrapers.pricing.Tmobile_Pricing_Postpaid_Tablets import tmo_scrape_postpaid_tablet_prices
from scrapers.pricing.Verizon_Pricing_Postpaid import ver_scrape_postpaid_smartphone_prices
from scrapers.pricing.Verizon_Pricing_Postpaid_Tablets import ver_scrape_postpaid_tablet_prices
import datetime
from data.model.Price import get_day_before
from scrapers.scraper_functions.Compare_Today_To_Yesterday_Promotions import generate_changes_report

today = datetime.datetime.now().date()
yesterday = get_day_before(today)

# print(datetime.datetime.now().time(), 'START')
#
# cri_scrape_prepaid_smartphone_prices()
# print(datetime.datetime.now().time(), '-> Cricket Prepaid Smartphones Complete')
# generate_changes_report('cricket', today, yesterday)
#
# tmo_scrape_postpaid_smartphone_prices()
# print(datetime.datetime.now().time(), '-> T-Mobile Postpaid Smartphones Complete')
# tmo_scrape_postpaid_tablet_prices()
# print(datetime.datetime.now().time(), '-> T-Mobile Postpaid Tablets Complete')
# generate_changes_report('tmobile', today, yesterday)
#
# spr_scrape_postpaid_smartphone_prices()
# print(datetime.datetime.now().time(),  '-> Sprint Postpaid Smartphones Complete')
spr_scrape_postpaid_tablet_prices()
print(datetime.datetime.now().time(), '-> Sprint Postpaid Tablets Complete')
generate_changes_report('sprint', today, yesterday)

met_scrape_prepaid_smartphone_prices()
print(datetime.datetime.now().time(), '-> MetroPCS Prepaid Smartphones Complete')
generate_changes_report('metropcs', today, yesterday)

att_scrape_postpaid_smartphone_prices()
print(datetime.datetime.now().time(), '-> AT&T Postpaid Smartphones Complete')
att_scrape_postpaid_tablet_prices()
print(datetime.datetime.now().time(), '-> AT&T Postpaid Tablets Complete')
generate_changes_report('att', today, yesterday)

att_scrape_prepaid_smartphone_prices()
print(datetime.datetime.now().time(), '-> AT&T Prepaid Smartphones Complete')

ver_scrape_postpaid_smartphone_prices()
print(datetime.datetime.now().time(), '-> Verizon Postpaid Smartphones Complete')
ver_scrape_postpaid_tablet_prices()
print(datetime.datetime.now().time(), '-> Verizon Postpaid Tablets Complete')
generate_changes_report('verizon', today, yesterday)

ver_scrape_prepaid_smartphone_prices()
print(datetime.datetime.now().time(), '-> Verizon Prepaid Smartphones Complete')

print(datetime.datetime.now().time(), 'END')
