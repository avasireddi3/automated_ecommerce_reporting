import json
import orjson
import urllib3
import cloudscraper
import traceback
import asyncio
from src.config import min_lat, min_long, max_lat, max_long, grid_detail, unknown_bar, auto_bar
from src.utils.data_models import Location
from src.utils.helper_functions import get_auth

def get_instamart_store(lat:float,long:float,headers:dict)->dict[str,any]:
    payload = {"data": {
        "lat": lat,
        "lng": long,
        "clientId": "INSTAMART-APP"
    }}
    payload = orjson.dumps(payload)
    session = urllib3.PoolManager()
    resp = session.request("POST", "https://www.swiggy.com/api/instamart/home/select-location", headers=headers, body=payload)
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
            platform="instamart",
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

def main():
    headers = asyncio.run(get_auth("https://www.swiggy.com/instamart",
                                   api_term="api/instamart",
                                   request_method="GET"))
    print(get_instamart_store(13.043437, 77.615263,
                              headers=headers))
    print(get_instamart_store(13.012609, 77.598899,
                              headers=headers))



if __name__=="__main__":
    main()