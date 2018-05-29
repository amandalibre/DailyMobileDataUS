from scrapers.promotions.Cricket_Promotions_Prepaid import cri_scrape_prepaid_promotions
from scrapers.promotions.Metropcs_Promotions_Prepaid import met_scrape_prepaid_promotions
from scrapers.promotions.Att_Promotions_Postpaid import att_scrape_postpaid_promotions
from scrapers.promotions.Sprint_Promotions_Postpaid import spr_scrape_postpaid_promotions
from scrapers.promotions.Tmobile_Promotions_Postpaid import tmo_scrape_postpaid_promotions
from scrapers.promotions.Verizon_Promotions_Postpaid import ver_scrape_postpaid_promotions

print('Prepaid:')
cri_scrape_prepaid_promotions()
print('-> Cricket Complete')
met_scrape_prepaid_promotions()
print('-> MetroPCS Complete')

print('Postpaid:')
att_scrape_postpaid_promotions()
print('-> AT&T Complete')
spr_scrape_postpaid_promotions()
print('-> Sprint Complete')
tmo_scrape_postpaid_promotions()
print('-> T-Mobile Complete')
ver_scrape_postpaid_promotions()
print('-> Verizon Complete')