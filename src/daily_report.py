from ecomScrapers import zepto_scraper, instamart_scraper, blinkit_scraper
from ecomScrapers.data_models import Listing
import csv

def generate_csv():
    with open('test.csv','w',newline='') as csvfile:
        fieldnames = Listing.model_fields.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for set_listings in zepto_scraper.scrape():
            writer.writerows(set_listings)
        for set_listings in instamart_scraper.scrape():
            writer.writerows(set_listings)
        for set_listings in blinkit_scraper.scrape():
            writer.writerows(set_listings)

if __name__ == "__main__":
    generate_csv()