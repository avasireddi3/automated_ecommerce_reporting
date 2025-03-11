import json
import time
import urllib.parse
import orjson
import urllib3
import asyncio
import datetime
import logging
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from src.utils import try_extract, Listing, queries, locations

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def on_request(data:InterceptedRequest):
    if "api/instamart/search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth():
    logger.info("Starting request for headers")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Important for Docker
    options.add_argument("--disable-gpu")
    options.headless=True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://www.swiggy.com/instamart/search?custom_back=true&query=idli+rava")
            await driver.sleep(2)

def get_response(query:str,location:str)->urllib3.response:
    logger.info("Getting response")
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

def extract_data(data:dict, query:str, loc:str)->Listing:
    logger.info("Extracting data")
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
        curr = Listing(
            platform="instamart",
            timestamp= datetime.datetime.now(),
            search_term=query,
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

def scrape_instamart():
    logger.info('Starting instamart scraper')
    asyncio.run(get_auth())
    logger.info('Headers in place')
    for location in locations:
        for query in queries:
            resp = get_response(query, location["instamart_id"])
            data = json.loads(resp.data)
            items = []
            for item in extract_data(data,query,location["name"]):
                items.append(item)
            time.sleep(0.5)
            logger.info(f"Recieved listings for {query} in {location["name"]}")
            yield items


if __name__ == '__main__':
    scrape()
