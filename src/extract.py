from src.ecomScrapers import zepto_scraper, instamart_scraper, blinkit_scraper
from src.utils import Listing
import csv

def generate_csv():
    with open('demo_files/test.csv','w',newline='') as csvfile:
        fieldnames = Listing.model_fields.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for set_listings in zepto_scraper.scrape_zepto():
            writer.writerows(set_listings)
        for set_listings in instamart_scraper.scrape_instamart():
            writer.writerows(set_listings)
        for set_listings in blinkit_scraper.scrape_blinkit():
            writer.writerows(set_listings)

if __name__ == "__main__":
    generate_csv()