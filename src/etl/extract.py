from src.ecomScrapers import zepto_scraper, instamart_scraper, blinkit_scraper
from src.utils import Listing
import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_csv()->None:
    """write results of scrapers into a csv file"""
    with open('demo_files/test.csv','w',newline='') as csvfile:
        fieldnames = Listing.model_fields.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for set_listings in zepto_scraper.scrape_zepto():
            writer.writerows(set_listings)
        logger.info("Extracted zepto")
        for set_listings in instamart_scraper.scrape_instamart():
            writer.writerows(set_listings)
        logger.info("Extracted instamart")
        for set_listings in blinkit_scraper.scrape_blinkit():
            writer.writerows(set_listings)
        logger.info("Extracted blinkit")

if __name__ == "__main__":
    generate_csv()