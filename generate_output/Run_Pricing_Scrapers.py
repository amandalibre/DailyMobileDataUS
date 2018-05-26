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

print('Prepaid:')
att_scrape_prepaid_smartphone_prices()
print('-> AT&T Complete')
cri_scrape_prepaid_smartphone_prices()
print('-> Cricket Complete')
met_scrape_prepaid_smartphone_prices()
print('-> MetroPCS Complete')
ver_scrape_prepaid_smartphone_prices()
print('-> Verizon Complete')

print('Postpaid:')
att_scrape_postpaid_smartphone_prices()
print('-> AT&T Smartphones Complete')
att_scrape_postpaid_tablet_prices()
print('-> AT&T Tablets Complete')
spr_scrape_postpaid_smartphone_prices()
print('-> Sprint Smartphones Complete')
spr_scrape_postpaid_tablet_prices()
print('-> Sprint Tablets Complete')
tmo_scrape_postpaid_smartphone_prices()
print('-> T-Mobile Smartphones Complete')
tmo_scrape_postpaid_tablet_prices()
print('-> T-Mobile Tablets Complete')
ver_scrape_postpaid_smartphone_prices()
print('-> Verizon Smartphones Complete')
ver_scrape_postpaid_tablet_prices()
print('-> Verizon Tablets Complete')
