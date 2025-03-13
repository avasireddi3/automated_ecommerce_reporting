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
    print(data.request.url)
    if "api/v2/get_page" in data.request.url and data.request.method=="GET":
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
            await driver.sleep(4)

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

def get_zepto_store(lat:float,long:float)->dict[str,any]:
    asyncio.run(get_auth("https://www.zepto.com/"))
    print(auth)
    params = {"latitude": str(lat), "longitude": str(long), "page_type": "HOME", "version": "v2",
                   "show_new_eta_banner": "false", "page_size": "1", "enforce_platform_type": "DESKTOP"}
    querystring = {"latitude": str(lat), "longitude": str(long)}
    session = urllib3.PoolManager()
    resp_store = session.request("GET",url="https://api.zepto.com/api/v2/get_page", headers=auth, fields=params)
    resp_geo = session.request("GET", "https://api.zepto.com/api/v1/maps/geocode", headers = auth, fields=querystring)

    try:
        data = json.loads(resp_store.data)
    except json.decoder.JSONDecodeError:
        print(resp_store.data,lat,long)
        data = None
    try:
        store_id = data["storeServiceableResponse"]["storeId"]
    except KeyError:
        print(traceback.format_exc())
        store_id = None
    except TypeError:
        print(traceback.format_exc())
        store_id = None
    try:
        geo_data = json.loads(resp_geo.data)
    except json.decoder.JSONDecodeError:
        print(resp_store.data, lat, long)
        geo_data = None
    try:
        locality=""
        for level in geo_data["results"][0]["address_components"]:
            if "sublocality_level_1" in level["types"]:
                locality = level["long_name"]
    except KeyError:
        locality = None
    except TypeError:
        locality = None
    if store_id and locality:
        curr = Location(
            store_id=store_id,
            locality=locality,
            latitude=lat,
            longitude=long
        )
        return curr.model_dump()




def main():
    # locations = []
    # plot_map = folium.Map(location=[12.9716, 77.5946], zoom_start=18)
    # with alive_bar(total = grid_detail**2,bar=auto_bar,force_tty=True) as bar:
    #     for lat in np.linspace(min_lat,max_lat,grid_detail):
    #         for long in np.linspace(min_long,max_long,grid_detail):
    #             lat = round(lat,3)
    #             long = round(long,3)
    #             store_details = get_instamart_store(float(lat),float(long))
    #             if store_details:
    #                 locations.append(store_details)
    #                 folium.Marker([store_details["latitude"],
    #                                store_details["longitude"]],).add_to(plot_map)
    #             bar()
    #             time.sleep(0.5)
    # df = pl.from_dicts(data = locations)
    # df = df.unique(subset=["store_id"])
    # plot_map.save('instamart_map.html')

    print(get_zepto_store(13.014269582274796,77.639510234551))




if __name__=="__main__":
    main()