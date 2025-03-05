import json
import orjson
from selenium_driverless import webdriver
import asyncio
from rich import print
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
import urllib3
from data_models import Listing
from helper_functions import  try_extract

async def on_request(data:InterceptedRequest):
    if "api/v3/search" in data.request.url and data.request.method=="POST":
        global auth
        try:
            auth = data.request.headers
        except KeyError:
            print("no auth header found in request")

async def main():
    options = webdriver.ChromeOptions()
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://www.zeptonow.com/search?query=idli+rava")
            await driver.sleep(2)


if __name__ == '__main__':
    asyncio.run(main())
    auth["storeId"] = "17141f08-6ccd-4d8b-ae18-0bd9ebbb8a40"
    auth["store_etas"] = """{"17141f08-6ccd-4d8b-ae18-0bd9ebbb8a40":8,"6b1d82f8-b2ea-4e43-ae70-6f6bca1ec77a":17}"""
    auth["store_id"] ="17141f08-6ccd-4d8b-ae18-0bd9ebbb8a40"
    auth["store_ids"] ="17141f08-6ccd-4d8b-ae18-0bd9ebbb8a40,6b1d82f8-b2ea-4e43-ae70-6f6bca1ec77a"
    payload = {"query":"idli rava","pageNumber":0,"userSessionId":auth["session_id"]}
    payload_str = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", "https://api.zeptonow.com/api/v3/search", headers=auth,body=payload_str)
    data = json.loads(resp.data)
    # with open("zepto_sample.txt", "w") as f:
    #     f.write(json.dumps(data,indent=2))
    for grid in data["layout"][1:-1]:
        for item in grid["data"]["resolver"]["data"]["items"]:
            product = item["productResponse"]
            mrp = int(try_extract(product,"mrp",0))/100
            price = int(try_extract(product,"sellingPrice",0))/100
            try:
                unit = str(try_extract(product["productVariant"], "weightInGms", "0")) + " g"
            except TypeError:
                unit = try_extract(product["l4Attributes"], "weight", "0 kg")
            name = try_extract(product["product"],"name","None")
            brand = try_extract(product["product"],"brand","None")
            try:
                cat = product["l3CategoriesDetail"][0]["name"]
            except TypeError:
                cat = "None"
            curr = Listing(
                mrp=mrp,
                price=price,
                unit=unit,
                brand=brand,
                name=name,
                cat=cat,
            )
            print(curr)

