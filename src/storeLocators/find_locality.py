import json
import urllib3
import traceback
from src.credentials import gmaps_api_key

def get_locality(lat:float,long:float,headers:dict):
    querystring = {"latitude": str(lat), "longitude": str(long)}
    session = urllib3.PoolManager()
    resp_geo = session.request("GET", "https://api.zepto.com/api/v1/maps/geocode", headers=headers, fields=querystring)
    locality_1=None
    locality_2=None
    try:
        geo_data = json.loads(resp_geo.data)
    except json.decoder.JSONDecodeError:
        geo_data = None
    try:
        locality=""
        for level in geo_data["results"][0]["address_components"]:
            if "sublocality_level_1" in level["types"]:
                locality_1 = level["long_name"]
            if "sublocality_level_2" in level["types"]:
                locality_2 = level["long_name"]
    except KeyError:
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    except TypeError:
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    if locality_1:
        locality = locality_1
    elif locality_2:
        locality = locality_2
    else:
        locality = ""
    return locality

def get_google_locality(lat:float,long:float):
    querystring = {"latlng":str(lat)+','+str(long),
                   "key":str(gmaps_api_key)}
    session = urllib3.PoolManager()
    resp_geo = session.request("GET", "https://maps.googleapis.com/maps/api/geocode/json", fields=querystring)
    locality_1 = None
    locality_2 = None
    try:
        geo_data = json.loads(resp_geo.data)

    except json.decoder.JSONDecodeError:
        geo_data = None
    try:
        locality = ""
        print(json.dumps(geo_data, indent=2))
        for level in geo_data["results"][0]["address_components"]:
            if "sublocality_level_1" in level["types"]:
                locality_1 = level["long_name"]
            if "sublocality_level_2" in level["types"]:
                locality_2 = level["long_name"]
    except KeyError:
        print(json.dumps(geo_data,indent=2))
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    except TypeError:
        print(json.dumps(geo_data, indent=2))
        traceback.print_exc()
        locality_1 = None
        locality_2 = None
    except IndexError:
        print(json.dumps(geo_data, indent=2))
    if locality_1:
        locality = locality_1
    elif locality_2:
        locality = locality_2
    else:
        locality = ""
    return locality

if __name__=="__main__":
    print(get_google_locality(12.9035, 77.717))