import json
import time
import orjson
import requests
import urllib3
import asyncio
import datetime
import logging
from collections.abc import Iterator
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from alive_progress import alive_bar
from urllib3 import BaseHTTPResponse

from src.config import unknown_bar, auto_bar
from src.utils import try_extract, Listing, queries, locations


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def on_request(data:InterceptedRequest)->None:
    """setting global variable auth with intercepted network request"""
    if "api/v3/search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth()->None:
    """getting fresh headers for a search session"""
    logger.debug("Starting request for headers")
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Important for Docker
    options.add_argument("--disable-gpu")
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://www.zeptonow.com/search?query=idli+rava")
            await driver.sleep(1)

def get_response(query:str,location:str)-> BaseHTTPResponse:
    """"getting response from backend api for a given query and response"""
    logger.debug("Getting response")
    auth["user-agent"] = "Mozilla/5.0(Linux; U; Android 2.2; en-gb; LG-P500 Build/FRF91) AppleWebKit/533.0 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
    auth["storeId"] = location
    auth["store_etas"] = """{"""+location+""":0}"""
    auth["store_id"] = location
    auth["store_ids"] = location
    payload = orjson.dumps({"query": query, "pageNumber": 0, "userSessionId": auth["session_id"]})
    session = urllib3.PoolManager()
    resp = session.request("POST", "https://api.zeptonow.com/api/v3/search", headers=auth, body=payload)
    return resp

def extract_data(data:dict,query:str,loc:str)->Iterator[dict]:
    """extract data from response that is passed in the form of a dictionary"""
    logger.debug("Extracting data")
    for grid in data["layout"][1:-1]:
        for item in grid["data"]["resolver"]["data"]["items"]:
            product = item["productResponse"]
            mrp = int(try_extract(product,"mrp",0))//100
            price = int(try_extract(product,"sellingPrice",0))//100
            unit = try_extract(product["productVariant"],"weightInGms",0)
            # try:
            #     unit = str(try_extract(product["productVariant"], "weightInGms", "0")) + " g"
            # except TypeError:
            #     unit = try_extract(product["l4Attributes"], "weight", "0 kg")
            name = try_extract(product["product"],"name","None")
            brand = try_extract(product["product"],"brand","None")
            try:
                cat = product["l3CategoriesDetail"][0]["name"]
            except TypeError:
                cat = "None"
            if product["meta"]["tags"][0]["type"]=="SPONSORED":
                ad = True
            else:
                ad = False
            rank = try_extract(item,"position",-1)
            curr = Listing(
                platform="zepto",
                timestamp=datetime.datetime.now(),
                search_term = query,
                location = loc,
                mrp=mrp,
                price=price,
                unit=unit,
                brand=brand,
                name=name,
                cat=cat,
                ad=ad,
                rank=rank
            )
            yield curr.model_dump()

def scrape_zepto()->Iterator[list]:
    """create new session and scrape for queries and location given in utils.constants.py"""
    with alive_bar(unknown=unknown_bar) as bar:
        bar()
        logger.info('Starting zepto scraper')
        asyncio.run(get_auth())
        logger.info("Initialized zepto scraper")
    logger.debug('Headers in place')
    with alive_bar(total=len(locations) * len(queries),bar=auto_bar) as bar:
        for location in locations:
            for query in queries:
                items = []
                resp = get_response(query, location["zepto_id"])
                data = json.loads(resp.data)
                for item in extract_data(data,query,location["name"]):
                    items.append(item)
                time.sleep(0.5)
                bar()
                logger.debug(f"Recieved listings for {query} in {location["name"]}")
                yield items



if __name__ == '__main__':
    scrape_zepto()



