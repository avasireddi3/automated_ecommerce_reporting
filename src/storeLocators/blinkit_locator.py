import json
import cloudscraper
import asyncio
import urllib
from src.utils.data_models import Location
from src.utils.helper_functions import get_auth

def get_blinkit_store(lat:float,long:float,headers:dict)->dict[str,any]:
    scraper = cloudscraper.create_scraper()
    querystring = {
        "filter": "new_offer,show_product_group_sharing,is_new_user,cart_ab_test_variant,city_id,sku_auto_add,cart_banner_image,show_referral_login,product_sku_limit",
        "offers_last_visit_ts": "0"}
    headers["lat"] = str(lat)
    headers["lon"] = str(long)
    base_url = "https://blinkit.com/v2/services/secondary-data"
    encoded_params = urllib.parse.urlencode(querystring)
    complete_url = f"{base_url}?{encoded_params}"
    resp = scraper.get(url=complete_url,headers=headers)
    data = json.loads(resp.text)
    # print(json.dumps(data,indent=2))
    try:
        store_id = str(data["analytics_properties"]["merchant_id"])
        locality = ""
        latitude = data["analytics_properties"]["latitude"]
        longitude = data["analytics_properties"]["longitude"]
        curr = Location(
            platform="blinkit",
            store_id=store_id,
            locality=locality,
            latitude=latitude,
            longitude=longitude
        )
        return curr.model_dump()
    except KeyError:
        pass
    except TypeError:
        pass




def main():
    headers = asyncio.run(get_auth("https://blinkit.com",
                                   api_term="v2/services/secondary-data",
                                   request_method="GET"))
    print(get_blinkit_store(13.061830, 77.587995,
                              headers=headers))


if __name__=="__main__":
    main()