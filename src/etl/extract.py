from src.etl.ecomScrapers import zepto_scraper, instamart_scraper, blinkit_scraper
from src.utils import Listing
from google.cloud import bigquery
import polars as pl
import csv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_locations():
    client = bigquery.Client(project="turnkey-triumph-453704-e8")
    query = """
        SELECT *
        FROM turnkey-triumph-453704-e8.test_dataset_1.store_locations
        LIMIT 1
    """
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    df = pl.from_pandas(df)
    dfs_split = df.partition_by(["platform"])
    results = {"zepto":[],
               "instamart":[],
               "blinkit":[]}
    for df in dfs_split:
        results[df["platform"].min()] = df.to_dicts()
    return results

def generate_csv(locations:dict)->None:
    """write results of scrapers into a csv file"""
    with open('demo_files/test.csv','w',newline='') as csvfile:
        fieldnames = Listing.model_fields.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for set_listings in zepto_scraper.scrape_zepto(locations["zepto"]):
            writer.writerows(set_listings)
        logger.info("Extracted zepto")
        for set_listings in instamart_scraper.scrape_instamart(locations["instamart"]):
            writer.writerows(set_listings)
        logger.info("Extracted instamart")
        for set_listings in blinkit_scraper.scrape_blinkit(locations["blinkit"]):
            writer.writerows(set_listings)
        logger.info("Extracted blinkit")

def extract_listings()->None:
    locations = get_locations()
    generate_csv(locations)