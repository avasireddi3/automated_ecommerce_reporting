import json
import urllib3
import asyncio
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
    try:
        geo_data = json.loads(resp_geo.data)
    except json.decoder.JSONDecodeError:
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
    return locality