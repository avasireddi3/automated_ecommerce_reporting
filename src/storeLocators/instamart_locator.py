import json
import orjson
import urllib3
import cloudscraper
import traceback
import asyncio
import urllib
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
import numpy as np
import time
import polars as pl
import folium
from alive_progress import alive_bar
from src.config import min_lat, min_long, max_lat, max_long, grid_detail, unknown_bar, auto_bar
from src.utils.data_models import Location

async def on_request(data:InterceptedRequest)->None:
    """setting global variable auth with intercepted network request"""
    if "api/instamart" in data.request.url and data.request.method=="GET":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth(url:str)->None:
    """getting fresh headers for a search session"""
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Important for Docker
    options.add_argument("--disable-gpu")
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get(url)
            await driver.sleep(2)

def get_instamart_store(lat:float,long:float)->dict[str,any]:
    asyncio.run(get_auth("https://www.swiggy.com/instamart"))
    payload = {"data": {
        "lat": lat,
        "lng": long,
        "clientId": "INSTAMART-APP"
    }}
    payload = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", "https://www.swiggy.com/api/instamart/home/select-location", headers=auth, body=payload)
    try:
        data = json.loads(resp.data)
    except json.decoder.JSONDecodeError:
        print(resp.data,lat,long)
        data = None
    try:
        store_details = data["data"]["storeDetails"]
        store_id = store_details["id"]
        locality = store_details["locality"]
        lat_long = store_details["lat_long"].split(",")
        curr= Location(
            store_id=store_id,
            locality=locality,
            latitude=lat_long[0],
            longitude=lat_long[1]
        )
        return curr.model_dump()
    except KeyError:
        pass
    except TypeError:
        pass

def main():
    print(get_instamart_store(13.014269582274796,77.639510234551))


if __name__=="__main__":
    main()