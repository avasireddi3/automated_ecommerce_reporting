import json

import orjson
from selenium_driverless import webdriver
import asyncio
from rich import print
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
import urllib3
from helper_functions import try_extract
from data_models import Listing

async def on_request(data:InterceptedRequest):
    if "api/instamart/search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def main():
    options = webdriver.ChromeOptions()
    options.headless=True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://www.swiggy.com/instamart/search?custom_back=true&query=idli+rava")
            await driver.sleep(2)


if __name__ == '__main__':
    asyncio.run(main())
    url = "https://www.swiggy.com/api/instamart/search?pageNumber=1&searchResultsOffset=0&limit=100&query=idli%20rava&ageConsent=false&pageType=INSTAMART_SEARCH_PAGE&isPreSearchTag=false&highConfidencePageNo=0&lowConfidencePageNo=0&voiceSearchTrackingId=&storeId=1390218&primaryStoreId=1390218&secondaryStoreId=1390218"
    payload = {"facets":{},"sortAttribute":""}
    payload_str = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", url=url, headers=auth,body=payload_str)
    data = json.loads(resp.data)
    # with open("instamart_sample.txt","w") as f:
    #     f.write(json.dumps(data,indent=2))=
    for item in data["data"]["widgets"][0]["data"]:
        product = item["variations"][0]
        mrp = try_extract(product["price"],"mrp",0)
        price = try_extract(product["price"],"store_price",0)
        unit = try_extract(product,"quantity","0 kg")
        brand = try_extract(product,"brand", "None")
        name = try_extract(product,"display_name","None")
        cat = try_extract(product,"sub_category_type","None")
        ads_data = try_extract(item,"sosAdsPositionData","None")
        if ads_data != "None":
            rank = ads_data["organic_rank"]
            if ads_data["ads_rank"]!=-1:
                ad = True
            else:
                ad = False
        else:
            ad = False
            rank=-1
        curr = Listing(
            mrp=mrp,
            price=price,
            unit=unit,
            brand=brand,
            name=name,
            cat=cat,
            ad = ad,
            rank = rank
        )
        print(curr)
