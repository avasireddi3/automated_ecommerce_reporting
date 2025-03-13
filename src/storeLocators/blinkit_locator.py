import json
import cloudscraper
import asyncio
import urllib
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from src.utils.data_models import Location
from src.storeLocators.find_locality import get_locality

async def on_request(data:InterceptedRequest)->None:
    """setting global variable auth with intercepted network request"""
    if "v2/services/secondary-data" in data.request.url and data.request.method=="GET":
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

def get_blinkit_store(lat:float,long:float)->dict[str,any]:
    scraper = cloudscraper.create_scraper()
    asyncio.run(get_auth("https://blinkit.com"))
    querystring = {
        "filter": "new_offer,show_product_group_sharing,is_new_user,cart_ab_test_variant,city_id,sku_auto_add,cart_banner_image,show_referral_login,product_sku_limit",
        "offers_last_visit_ts": "0"}
    auth["lat"] = str(lat)
    auth["lon"] = str(long)
    base_url = "https://blinkit.com/v2/services/secondary-data"
    encoded_params = urllib.parse.urlencode(querystring)
    complete_url = f"{base_url}?{encoded_params}"
    resp = scraper.get(url=complete_url,headers=auth)
    data = json.loads(resp.text)
    store_id = str(data["analytics_properties"]["merchant_id"])
    locality = get_locality(lat,long)
    latitude = data["analytics_properties"]["latitude"]
    longitude = data["analytics_properties"]["longitude"]
    curr = Location(
        store_id=store_id,
        locality=locality,
        latitude=latitude,
        longitude=longitude
    )
    return curr



def main():
    print(get_blinkit_store(13.043437, 77.615263))


if __name__=="__main__":
    main()