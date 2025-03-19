import json
import asyncio
import cloudscraper
import urllib
import time
import requests.models
import datetime
import logging
from collections.abc import Iterator
from alive_progress import alive_bar
from src.utils import try_extract, Listing, queries, locations, parse_weight, get_auth
from src.config import auto_bar,unknown_bar

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_response(query:str,location:dict,auth:dict)->requests.models.Response:
    """"getting response from backend api for a given query and response"""
    logger.debug("Getting response")
    scraper = cloudscraper.create_scraper()
    auth["lat"] = str(location["latitude"])
    auth["lon"] = str(location["longitude"])
    params = {
        "start":"0",
        "size":"20",
        "search_type":"7",
        "q":query
    }
    base_url = "https://blinkit.com/v6/search/products"
    encoded_params = urllib.parse.urlencode(params)
    complete_url = f"{base_url}?{encoded_params}"
    resp = scraper.get(url=complete_url,
                       headers=auth)
    return resp

def extract_data(data:dict,query:str, store_id:str, loc:str)->Iterator[dict]:
    """extract data from response that is passed in the form of a dictionary"""
    logger.debug("Extracting data")
    for i,listing in enumerate(data["products"]):
        mrp = try_extract(listing,"mrp",0)
        price = try_extract(listing,"price",0)
        unit = try_extract(listing,"unit","0 kg")
        unit = parse_weight(unit)
        brand = try_extract(listing,"brand","None")
        name = try_extract(listing,"name","None")
        cat = try_extract(listing, "type", "None")
        ad = try_extract(listing, "is_boosted",False)
        rank = i
        dt = datetime.datetime.now()
        dt = datetime.datetime.strptime(str(dt).split(".")[0], "%Y-%m-%d %H:%M:%S")
        curr = Listing(
            platform="blinkit",
            timestamp=dt,
            search_term=query,
            store_id=store_id,
            location=loc,
            mrp = mrp,
            price = price,
            unit = unit,
            brand = brand,
            name = name,
            cat = cat,
            ad = ad,
            rank = rank
        )
        yield curr.model_dump()

def scrape_blinkit(locations:list[dict])->Iterator[list]:
    """create new session and scrape for queries and location given in utils.constants.py"""
    with alive_bar(unknown=unknown_bar) as bar:
        logger.info('Starting blinkit scraper')
        bar()
        headers = asyncio.run(get_auth(url="https://blinkit.com/s/?q=idli%20rava",
                                       api_term="search",
                                       request_method="GET"))
        logger.info("Initialized blinkit scraper")
    logger.debug('Headers in place')
    cnt=0
    with alive_bar(total = len(locations)*len(queries),bar=auto_bar) as bar:
        for location in locations:
            for query in queries:
                items = []
                resp = get_response(query, location,headers)
                data = json.loads(resp.text)
                for item in extract_data(data,query,location["store_id"],location["locality"]):
                    items.append(item)
                time.sleep(0.5)
                bar()
                logger.debug(f"Recieved listings for {query} in {location["locality"]}")
                yield items

if __name__ == '__main__':
    for item in scrape_blinkit():
        print(item)









