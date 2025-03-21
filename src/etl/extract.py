import os

from src.etl.ecomScrapers import zepto_scraper, instamart_scraper, blinkit_scraper
from src.utils import Listing
from google.cloud import bigquery
from dotenv import load_dotenv
import polars as pl
import csv
import logging
from src.config import locations
from src.utils.validators import check_path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv("secrets.env")

def get_locations():
    load_dotenv("secrets.env")
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    client = bigquery.Client(project=project_id)
    query = f"""
        SELECT * 
        FROM {project_id}.test_dataset_1.store_locations
        WHERE locality IN UNNEST(@locations)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("locations", "STRING", locations)  # Pass localities as an array
        ]
    )

    query_job = client.query(query,job_config=job_config)
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

def extract_listings(stage_path:str="staging_data/stage.csv")->None:
    locations = get_locations()
    check_path(stage_path)
    with open(stage_path, 'w', newline='') as csvfile:
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

if __name__ == "__main__":
    print(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
    locations = get_locations()
    for platform in locations:
        for store in locations[platform]:
            print(store)
