import json
import urllib3
import asyncio
import traceback
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest

async def on_request(data:InterceptedRequest)->None:
    """setting global variable auth with intercepted network request"""
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
            await driver.sleep(2)

def get_locality(lat:float,long:float):
    asyncio.run(get_auth("https://www.zepto.com/"))
    querystring = {"latitude": str(lat), "longitude": str(long)}
    session = urllib3.PoolManager()
    resp_geo = session.request("GET", "https://api.zepto.com/api/v1/maps/geocode", headers=auth, fields=querystring)
    locality_1=None
    locality_2=None
    try:
        geo_data = json.loads(resp_geo.data)
    except json.decoder.JSONDecodeError:
        geo_data = None
    try:
        locality=""
        for level in geo_data["results"][0]["address_components"]:
            if "sublocality_level_1" in level["types"]:
                locality_1 = level["long_name"]
            if "sublocality_level_2" in level["types"]:
                locality_2 = level["long_name"]
    except KeyError:
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    except TypeError:
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    if locality_1:
        locality = locality_1
    elif locality_2:
        locality = locality_2
    else:
        locality = ""
    return locality