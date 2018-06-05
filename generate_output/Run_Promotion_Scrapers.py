from scrapers.promotions.Cricket_Promotions_Prepaid import cri_scrape_prepaid_promotions
from scrapers.promotions.Metropcs_Promotions_Prepaid import met_scrape_prepaid_promotions
from scrapers.promotions.Att_Promotions_Postpaid import att_scrape_postpaid_promotions
from scrapers.promotions.Sprint_Promotions_Postpaid import spr_scrape_postpaid_promotions
from scrapers.promotions.Tmobile_Promotions_Postpaid import tmo_scrape_postpaid_promotions
from scrapers.promotions.Verizon_Promotions_Postpaid import ver_scrape_postpaid_promotions
from scrapers.scraper_functions.Compare_Today_To_Yesterday_Promotions import generate_changes_report
import datetime
from data.model.Price import get_day_before

today = datetime.datetime.now().date()
yesterday = get_day_before(today)

print(datetime.datetime.now().time())
cri_scrape_prepaid_promotions()
print('-> Cricket Prepaid Complete')
print(datetime.datetime.now().time())
tmo_scrape_postpaid_promotions()
print('-> T-Mobile Postpaid Complete')
generate_changes_report('tmobile', today, yesterday)
print(datetime.datetime.now().time())
spr_scrape_postpaid_promotions()
print('-> Sprint Postpaid Complete')
generate_changes_report('sprint', today, yesterday)
print(datetime.datetime.now().time())
met_scrape_prepaid_promotions()
print('-> MetroPCS Prepaid Complete')
generate_changes_report('metropcs', today, yesterday)
print(datetime.datetime.now().time())
att_scrape_postpaid_promotions()
print('-> AT&T Postpaid Complete')
generate_changes_report('att', today, yesterday)
print(datetime.datetime.now().time())
ver_scrape_postpaid_promotions()
print('-> Verizon Postpaid Complete')
generate_changes_report('verizon', today, yesterday)
print(datetime.datetime.now().time())