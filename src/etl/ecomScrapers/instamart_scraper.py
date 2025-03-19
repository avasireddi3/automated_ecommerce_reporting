import json
import time
import urllib.parse
import orjson
import urllib3
import asyncio
import datetime
import logging
from collections.abc import Iterator
from src.config import unknown_bar, auto_bar
from src.utils import try_extract, Listing, queries,get_auth
from alive_progress import alive_bar


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_response(query:str,location:str,auth:dict)->urllib3.response:
    """"getting response from backend api for a given query,location and set of headers"""
    logger.debug("Getting response")
    params = {"pageNumber": "0",
              "searchResultsOffset": "0",
              "limit": "40",
              "query": query,
              "ageConsent": "false",
              "pageType": "INSTAMART_SEARCH_PAGE",
              "isPreSearchTag": "false",
              "highConfidencePageNo": "0",
              "lowConfidencePageNo": "0",
              "voiceSearchTrackingId": "",
              "storeId": location,
              "primaryStoreId": location,
              "secondaryStoreId": location}
    base_url = "https://www.swiggy.com/api/instamart/search"
    # Use the urllib3 urlencode function to encode the query parameters
    encoded_params = urllib.parse.urlencode(params)
    # Combine the base URL and encoded query parameters to form the complete URL
    complete_url = f"{base_url}?{encoded_params}"
    payload = {
        "facets": {},
        "sortAttribute": ""
    }
    payload = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", url=complete_url, headers=auth, body=payload)
    return resp

def extract_data(data:dict, query:str, store_id:str, loc:str)->Iterator[dict]:
    """extract data from response that is passed in the form of a dictionary"""
    logger.debug("Extracting data")
    for i,item in enumerate(data["data"]["widgets"][0]["data"]):
        product = item["variations"][0]
        mrp = try_extract(product["price"],"store_price",0)
        price = try_extract(product["price"],"offer_price",0)
        unit = try_extract(product,"weight_in_grams",0)
        brand = try_extract(product,"brand", "None")
        name = try_extract(product,"display_name","None")
        cat = try_extract(product,"sub_category_type","None")
        ads_data = try_extract(item,"sosAdsPositionData","None")
        if ads_data and ads_data!="None":
            adrank = try_extract(ads_data,"ads_rank",-1)
            if adrank!=-1:
                ad = True
            else:
                ad = False
        else:
            ad = False
        dt = datetime.datetime.now()
        dt = datetime.datetime.strptime(str(dt).split(".")[0], "%Y-%m-%d %H:%M:%S")
        curr = Listing(
            platform="instamart",
            timestamp= dt,
            search_term=query,
            store_id=store_id,
            location=loc,
            mrp=mrp,
            price=price,
            unit=unit,
            brand=brand,
            name=name,
            cat=cat,
            ad = ad,
            rank = i,
        )
        yield curr.model_dump()

def scrape_instamart(locations:list[dict])->Iterator[list]:
    """create new session and scrape for queries and location given in utils.constants.py"""
    with alive_bar(unknown=unknown_bar) as bar:
        bar()
        logger.info('Starting instamart scraper')
        headers = asyncio.run(get_auth(url="https://www.swiggy.com/instamart/search?custom_back=true&query=idli+rava",
                             api_term="api/instamart/search",
                             request_method="POST"))
        logger.info("Initialized instamart scraper")
    logger.debug('Headers in place')
    with alive_bar(total = len(locations)*len(queries), bar=auto_bar) as bar:
        for location in locations:
            for query in queries:
                resp = get_response(query, location["store_id"],headers)
                data = json.loads(resp.data)
                items = []
                for item in extract_data(data,query,location["store_id"],location["locality"]):
                    items.append(item)
                time.sleep(0.5)
                bar()
                logger.debug(f"Recieved listings for {query} in {location["locality"]}")
                yield items


if __name__ == '__main__':
    for item in scrape_instamart():
        for listing in item:
            print(listing)
