import json
import asyncio
import cloudscraper
import urllib
import time
import requests.models
import datetime
import logging
from collections.abc import Iterator
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from alive_progress import alive_bar
from src.utils import try_extract, Listing, queries, locations, parse_weight
from src.config import auto_bar,unknown_bar

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def on_request(data:InterceptedRequest)->None:
    """setting global variable auth with intercepted network request"""
    if "search" in data.request.url and data.request.method=="GET":
        global auth
        try:
            if data.request.headers["auth_key"]:
                auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth()->None:
    """getting fresh headers for a search session"""
    logger.debug("Starting request for blinkit headers")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Important for Docker
    options.add_argument("--disable-gpu")
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://blinkit.com/s/?q=idli%20rava")
            await driver.sleep(2)

def get_response(query:str,location:dict)->requests.models.Response:
    """"getting response from backend api for a given query and response"""
    logger.debug("Getting response")
    scraper = cloudscraper.create_scraper()
    auth["lat"] = location["lat"]
    auth["lon"] = location["lon"]
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

def extract_data(data:dict,query:str, loc:str)->Iterator[dict]:
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
        curr = Listing(
            platform="blinkit",
            timestamp=datetime.datetime.now(),
            search_term=query,
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

def scrape_blinkit()->Iterator[list]:
    """create new session and scrape for queries and location given in utils.constants.py"""
    with alive_bar(unknown=unknown_bar) as bar:
        logger.info('Starting blinkit scraper')
        bar()
        asyncio.run(get_auth())
        logger.info("Initialized blinkit scraper")
    logger.debug('Headers in place')
    cnt=0
    with alive_bar(total = len(locations)*len(queries),bar=auto_bar) as bar:
        for location in locations:
            for query in queries:
                items = []
                resp = get_response(query, location)
                data = json.loads(resp.text)
                for item in extract_data(data,query,location["name"]):
                    items.append(item)
                time.sleep(0.5)
                bar()
                logger.debug(f"Recieved listings for {query} in {location["name"]}")
                yield items

if __name__ == '__main__':
    asyncio.run(get_auth())
    scraper = cloudscraper.create_scraper()
    base_url = "https://blinkit.com/v2/services/secondary-data"
    resp = scraper.get(url=base_url, headers=auth)
    print(resp.text)









