import json
import urllib3
import asyncio
from src.utils.data_models import Location
from src.utils.helper_functions import get_auth

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
        store_id = None
    except TypeError:
        store_id = None

    locality = ""

    if store_id:
        curr = Location(
            platform="zepto",
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