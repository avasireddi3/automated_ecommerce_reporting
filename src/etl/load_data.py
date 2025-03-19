import polars as pl
import pandas as pd
import xlsxwriter
from config import uri, table_name, xlsx_file_name, colors_hex
from google.cloud import bigquery
import pyarrow as pa


def write_db(data:pl.dataframe)->None:
    """write to database located at the uri in config.py"""
    data.write_database(table_name=table_name,connection=uri,
                        if_table_exists="append")

def split_tables_sheet(data:pl.dataframe)->pl.dataframe:
    """split data into tables by platform for insertion into excel sheet"""
    dataframes = data.select(["platform",
                   "timestamp",
                   "search_term",
                   "brand",
                   "product_name",
                   "mrp",
                   "price",
                   "unit",
                   "ppu",
                   "discount_pct"]).partition_by(["platform"])
    for frame in dataframes:
        yield frame

def write_excel(data:pl.dataframe)->None:
    """write data to xlsx file"""
    row_count = {}
    with xlsxwriter.Workbook(f"demo_files/{xlsx_file_name}.xlsx",
                             {'nan_inf_to_errors':True}) as f:
        for frame in split_tables_sheet(data):
            print(frame)
            sheet = frame["platform"].min()
            # if sheet in row_count:
            #     position = "A" + str(row_count[sheet])
            #     row_count[sheet] += frame.shape[0] + 2
            # else:
            #     position = "A1"
            #     row_count[sheet] = frame.shape[0] + 3
            header_format = {
                "font_color" : colors_hex[sheet]["text"],
                "bold":True,
                "bg_color":colors_hex[sheet]["bg"]
            }
            frame.write_excel(f, sheet,
                              position="A1",
                              autofit=True,
                              header_format=header_format,
                              hide_gridlines=False,
                              )

def write_big_query(data:pl.dataframe)->None:
    client = bigquery.Client("turnkey-triumph-453704-e8")
    df = data.to_pandas(date_as_object=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Kolkata")
    table_id = "turnkey-triumph-453704-e8.test_dataset_1.test_listings"
    job = client.load_table_from_dataframe(df,table_id)
    job.result()
