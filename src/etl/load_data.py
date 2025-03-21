import polars as pl
import pandas as pd
import os
from dotenv import load_dotenv
from src.config import uri, table_name
from google.cloud import bigquery


load_dotenv("secrets.env")

def write_db(data:pl.dataframe)->None:
    """write to database located at the uri in config.py"""
    data.write_database(table_name=table_name,connection=uri,
                        if_table_exists="append")

def write_big_query(data:pl.dataframe)->None:
    client = bigquery.Client("turnkey-triumph-453704-e8")
    df = data.to_pandas(date_as_object=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Kolkata")
    table_id = "turnkey-triumph-453704-e8.test_dataset_1.test_listings"
    job = client.load_table_from_dataframe(df,table_id)
    job.result()

if __name__=="__main__":
    print(f"Google Credentials: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
