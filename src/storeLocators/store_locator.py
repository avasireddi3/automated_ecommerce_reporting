import traceback

import numpy as np
import time
import polars as pl
import folium
import asyncio
import logging
from alive_progress import alive_bar
from src.config import min_lat, min_long, max_lat, max_long, grid_detail, auto_bar, unknown_bar
from src.storeLocators.blinkit_locator import get_blinkit_store
from src.storeLocators.find_locality import get_google_locality
from src.utils.helper_functions import get_auth
from src.storeLocators.instamart_locator import get_instamart_store
from src.storeLocators.zepto_locator import get_zepto_store
from google.cloud import bigquery

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_locations_df(store_locators:list[dict])->pl.dataframe:
    locations = []
    logger.info("Scanning Locations")
    with alive_bar(total=(grid_detail ** 2)*len(store_locators), bar=auto_bar, force_tty=True) as bar:
        for lat in np.linspace(min_lat, max_lat, grid_detail):
            for long in np.linspace(min_long, max_long, grid_detail):
                lat = round(lat, 3)
                long = round(long, 3)
                # locality = get_locality(lat, long, store_locators[2]["headers"])
                for store_locator in store_locators:
                    store_details = store_locator["locator"](float(lat), float(long),
                                                             headers=store_locator["headers"])
                    if store_details:
                        # if store_details["locality"] == "":
                        #     store_details["locality"] = locality
                        locations.append(store_details)
                    bar()
                time.sleep(0.5)
    df = pl.from_dicts(data=locations)
    logger.info("Locations Scanned")
    return df

def process_locations(df:pl.dataframe)->np.ndarray:
    df_agg = df.group_by("store_id").agg(
        pl.col("platform").mode(),
        pl.col("latitude").mean(),
        pl.col("longitude").mean(),
        pl.col("locality").mode()
    )
    df_agg = df_agg.with_columns(
        pl.col("platform").list.get(0, null_on_oob=True),
        pl.col("locality").list.get(0, null_on_oob=True))
    coords = df_agg.to_numpy()
    return coords

def fill_locality(coords:np.ndarray)->np.ndarray:
    for coord in coords:
        try:
            coord[4] = get_google_locality(coord[2],coord[3])
            time.sleep(0.01)
        except IndexError:
            print(coord)
            traceback.print_exc()
            coord[4] = "None"
    return coords

def plot_map(coords:np.ndarray,icon:str,file_name:str)->None:
    plot_map = folium.Map(location=[12.9716, 77.5946], zoom_start=8)
    for coord in coords:
        if coord[1] == "instamart":
            color = "orange"
        elif coord[1] == "zepto":
            color = "darkpurple"
        elif coord[1] =="blinkit":
            color = "green"
        else:
            color = "black"
        folium.Marker(location=coord[2:4],
                      popup=coord[0],
                      tooltip=coord[4],
                      icon=folium.Icon(color=color, icon=icon)).add_to(plot_map)
    plot_map.save(f'{file_name}.html')

def upload_database(df:pl.dataframe)->None:
    client = bigquery.Client(project="turnkey-triumph-453704-e8")
    df = df.to_pandas(date_as_object=False)
    table_id = "turnkey-triumph-453704-e8.test_dataset_1.store_locations"
    job = client.load_table_from_dataframe(df, table_id)
    job.result()

def scan_stores():

    with alive_bar(total = 3, bar=auto_bar) as bar:
        logger.info("Requesting Headers")
        instamart_headers = asyncio.run(get_auth("https://www.swiggy.com/instamart",
                                                 api_term="api/instamart",
                                                 request_method="GET"))
        bar()
        zepto_headers = asyncio.run(get_auth("https://www.zepto.com/",
                                    api_term="api/v2/get_page",
                                    request_method="GET"))
        bar()
        blinkit_headers = asyncio.run(get_auth("https://blinkit.com",
                                       api_term="v2/services/secondary-data",
                                       request_method="GET"))
        bar()
        logger.info("Recieved Headers")

    store_locators = [
        {"locator":get_instamart_store,"headers":instamart_headers},
        {"locator": get_blinkit_store, "headers": blinkit_headers},
        {"locator": get_zepto_store, "headers": zepto_headers},
    ]

    df = get_locations_df(store_locators)
    coords = process_locations(df)
    coords = fill_locality(coords)
    coords = coords.tolist()
    schema = {
        "store_id":pl.datatypes.String,
        "platform":pl.datatypes.String,
        "latitude":pl.datatypes.Float64,
        "longitude":pl.datatypes.Float64,
        "locality":pl.datatypes.String
    }
    df = pl.DataFrame(coords,schema=schema,orient="row")
    upload_database(df)
    df.write_csv("store_locations.csv")
    plot_map(coords,"info","test_map")




if __name__=="__main__":
    scan_stores()