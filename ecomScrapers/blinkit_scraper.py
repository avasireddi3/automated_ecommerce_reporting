import json
import asyncio
import cloudscraper
import urllib
import requests.models
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from data_models import Listing
from helper_functions import try_extract


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

def get_response(query:str)->requests.models.Response:
    scraper = cloudscraper.create_scraper()
    auth["lat"] = "13.0159044"
    auth["lon"] = "77.63786189999999"
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
    print(type(resp))
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
        yield curr

if __name__ == '__main__':
    asyncio.run(get_auth())
    resp = get_response("chips")
    data = json.loads(resp.text)
    for item in extract_data(data):
        print(item)







