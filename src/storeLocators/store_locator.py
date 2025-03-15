import numpy as np
import time
import polars as pl
import folium
from alive_progress import alive_bar
from src.config import min_lat, min_long, max_lat, max_long, grid_detail, unknown_bar, auto_bar
from src.storeLocators.instamart_locator import get_instamart_store




def main():
    locations = []
    plot_map = folium.Map(location=[12.9716, 77.5946], zoom_start=18)
    with alive_bar(total = grid_detail**2,bar=auto_bar,force_tty=True) as bar:
        for lat in np.linspace(min_lat,max_lat,grid_detail):
            for long in np.linspace(min_long,max_long,grid_detail):
                lat = round(lat,3)
                long = round(long,3)
                store_details = get_instamart_store(float(lat),float(long))
                if store_details:
                    locations.append(store_details)
                    folium.Marker([store_details["latitude"],
                                   store_details["longitude"]],).add_to(plot_map)
                bar()
                time.sleep(0.5)
    df = pl.from_dicts(data = locations)
    df = df.unique(subset=["store_id"])
    plot_map.save('instamart_map.html')




if __name__=="__main__":
    main()