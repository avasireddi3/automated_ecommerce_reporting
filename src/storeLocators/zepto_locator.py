import json
import urllib3
import traceback
import asyncio
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from src.utils.data_models import Location
from src.utils.helper_functions import get_auth
from src.storeLocators.find_locality import get_locality

# async def on_request(data:InterceptedRequest)->None:
#     """setting global variable auth with intercepted network request"""
#     if "api/v2/get_page" in data.request.url and data.request.method=="GET":
#         global auth
#         try:
#             auth = data.request.headers
#         except KeyError:
#             print("no auth header found in request")
#
# async def get_auth(url:str)->None:
#     """getting fresh headers for a search session"""
#     options = webdriver.ChromeOptions()
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")  # Important for Docker
#     options.add_argument("--disable-gpu")
#     options.headless = True
#     async with webdriver.Chrome(options=options) as driver:
#         async with NetworkInterceptor(driver,on_request=on_request):
#             await driver.get(url)
#             await driver.sleep(2)

def get_zepto_store(lat:float,long:float,headers:dict)->dict[str,any]:
    params = {"latitude": str(lat), "longitude": str(long), "page_type": "HOME", "version": "v2",
                   "show_new_eta_banner": "false", "page_size": "1", "enforce_platform_type": "DESKTOP"}
    session = urllib3.PoolManager()
    resp_store = session.request("GET",url="https://api.zepto.com/api/v2/get_page", headers=headers, fields=params)
    try:
        data = json.loads(resp_store.data)
    except json.decoder.JSONDecodeError:
        data = None
    try:
        store_id = data["storeServiceableResponse"]["storeId"]
    except KeyError:
        print(traceback.format_exc())
        store_id = None
    except TypeError:
        print(traceback.format_exc())
        store_id = None

    locality = get_locality(lat,long)

    if store_id and locality:
        curr = Location(
            store_id=store_id,
            locality=locality,
            latitude=lat,
            longitude=long
        )
        return curr.model_dump()

def main():
    headers = asyncio.run(get_auth("https://www.zepto.com/",
                         api_term="api/v2/get_page",
                         request_method="GET"))
    print(get_zepto_store(13.014269582274796,77.639510234551,
                          headers = headers))
    print(get_zepto_store(13.061830, 77.587995,
                            headers=headers))




if __name__=="__main__":
    main()