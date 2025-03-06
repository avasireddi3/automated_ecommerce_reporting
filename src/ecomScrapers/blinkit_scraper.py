import json
import asyncio
import cloudscraper
import urllib
import time
import requests.models
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from ecomScrapers.data_models import Listing
from ecomScrapers.helper_functions import try_extract
from ecomScrapers.constants import locations, queries


async def on_request(data:InterceptedRequest):
    if "search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            if data.request.headers["auth_key"]:
                auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth():
    options = webdriver.ChromeOptions()
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://blinkit.com/s/?q=idli%20rava")
            await driver.sleep(2)

def get_response(query:str,location:dict)->requests.models.Response:
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

def extract_data(data:dict)->Listing:
    for i,listing in enumerate(data["products"]):
        mrp = try_extract(listing,"mrp",0)
        price = try_extract(listing,"price",0)
        unit = try_extract(listing,"unit","0 kg")
        brand = try_extract(listing,"brand","None")
        name = try_extract(listing,"name","None")
        cat = try_extract(listing, "type", "None")
        ad = try_extract(listing, "is_boosted",False)
        rank = i
        curr = Listing(
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

def scrape():
    asyncio.run(get_auth())
    for location in locations:
        for query in queries:
            items = []
            print(query, location["name"])
            resp = get_response(query, location)
            data = json.loads(resp.text)
            for item in extract_data(data):
                items.append(item)
            time.sleep(0.5)
            yield items

if __name__ == '__main__':
    scrape()







