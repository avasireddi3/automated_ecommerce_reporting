import json
import time
import urllib.parse
import orjson
import urllib3
import asyncio
from selenium_driverless import webdriver
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
from rich import print
from ecomScrapers.helper_functions import try_extract
from ecomScrapers.data_models import Listing
from ecomScrapers.constants import queries, locations

async def on_request(data:InterceptedRequest):
    if "api/instamart/search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def get_auth():
    options = webdriver.ChromeOptions()
    options.headless=True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://www.swiggy.com/instamart/search?custom_back=true&query=idli+rava")
            await driver.sleep(2)

def get_response(query:str,location:str)->urllib3.response:
    params = {"pageNumber": "0",
              "searchResultsOffset": "0",
              "limit": "40",
              "query": query,
              "ageConsent": "false",
              "pageType": "INSTAMART_SEARCH_PAGE",
              "isPreSearchTag": "false",
              "highConfidencePageNo": "0",
              "lowConfidencePageNo": "0",
              "voiceSearchTrackingId": "",
              "storeId": location,
              "primaryStoreId": location,
              "secondaryStoreId": location}
    base_url = "https://www.swiggy.com/api/instamart/search"
    # Use the urllib3 urlencode function to encode the query parameters
    encoded_params = urllib.parse.urlencode(params)
    # Combine the base URL and encoded query parameters to form the complete URL
    complete_url = f"{base_url}?{encoded_params}"
    payload = {
        "facets": {},
        "sortAttribute": ""
    }
    payload = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", url=complete_url, headers=auth, body=payload)
    return resp

def extract_data(data:dict)->Listing:
    for item in data["data"]["widgets"][0]["data"]:
        product = item["variations"][0]
        mrp = try_extract(product["price"],"mrp",0)
        price = try_extract(product["price"],"store_price",0)
        unit = try_extract(product,"quantity","0 kg")
        brand = try_extract(product,"brand", "None")
        name = try_extract(product,"display_name","None")
        cat = try_extract(product,"sub_category_type","None")
        rank = try_extract(item,"retrievalRank",-1)
        ads_data = try_extract(item,"sosAdsPositionData","None")
        if ads_data and ads_data!="None":
            adrank = try_extract(ads_data,"ads_rank",-1)
            if adrank!=-1:
                ad = True
            else:
                ad = False
        else:
            ad = False
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
        yield curr.model_dump()

def scrape():
    asyncio.run(get_auth())
    for location in locations:
        for query in queries:
            print(query, location["name"])
            resp = get_response(query, location["instamart_id"])
            data = json.loads(resp.data)
            items = []
            for item in extract_data(data):
                items.append(item)
            yield items
            time.sleep(0.5)

if __name__ == '__main__':
    scrape()

    # print("poha", locations[0]["name"])
    # resp = get_response("poha", locations[0]["instamart_id"])
    # data = json.loads(resp.data)
    # with open("../zepto_sample.txt","w") as f:
    #     f.write(json.dumps(data,indent=2))