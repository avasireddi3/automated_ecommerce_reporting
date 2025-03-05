import json
from selenium_driverless import webdriver
import asyncio
from rich import print
from selenium_driverless.scripts.network_interceptor import NetworkInterceptor, InterceptedRequest
import cloudscraper
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

async def main():
    options = webdriver.ChromeOptions()
    options.headless = True
    async with webdriver.Chrome(options=options) as driver:
        async with NetworkInterceptor(driver,on_request=on_request):
            await driver.get("https://blinkit.com/s/?q=idli%20rava")
            await driver.sleep(2)




if __name__ == '__main__':
    asyncio.run(main())
    scraper = cloudscraper.create_scraper()
    auth["lat"] = "13.0159044"
    auth["lon"] = "77.63786189999999"
    # resp = scraper.get(url = "https://blinkit.com/v6/search/products?start=0&size=50&search_type=7&q=idli%20rava", headers=auth)
    resp = scraper.get(url="https://blinkit.com/v6/search/products?q=idli%20rava&size=20&start=0&search_type=7&similar=true&search_count=20",
                       headers=auth)
    data = json.loads(resp.text)
    # with open("blinkit_sample.txt", "w") as f:
    #     f.write(json.dumps(data, indent=2))
    for listing in data["products"]:
        mrp = try_extract(listing,"mrp",0)
        price = try_extract(listing,"price",0)
        unit = try_extract(listing,"unit","0 kg")
        brand = try_extract(listing,"brand","None")
        name = try_extract(listing,"name","None")
        cat = try_extract(listing, "type", "None")
        curr = Listing(
            mrp = mrp,
            price = price,
            unit = unit,
            brand = brand,
            name = name,
            cat = cat,
        )
        print(curr)






