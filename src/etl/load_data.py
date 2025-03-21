import polars as pl
import pandas as pd
import os
from dotenv import load_dotenv
from src.config import uri, table_name
from google.cloud import bigquery

from src.utils.validators import validate_db_connection, validate_bigquery_connection

load_dotenv("secrets.env")

def write_db(data:pl.dataframe)->None:
    """write to database located at the uri in config.py"""
    validate_db_connection(uri)
    data.write_database(table_name=table_name,connection=uri,
                        if_table_exists="append")

def write_big_query(data:pl.dataframe)->None:
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    validate_bigquery_connection(project_id)
    client = bigquery.Client(project_id)
    df = data.to_pandas(date_as_object=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Kolkata")
    table_id = project_id+".test_dataset_1.test_listings"
    job = client.load_table_from_dataframe(df,table_id)
    job.result()

if __name__=="__main__":
    validate_bigquery_connection("dummy")