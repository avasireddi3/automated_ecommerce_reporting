import polars as pl
import xlsxwriter
from src.config import uri, table_name, xlsx_file_name, colors_hex



def write_db(data:pl.dataframe):
    data.write_database(table_name=table_name,connection=uri,
                        if_table_exists="append")

def split_tables_sheet(data:pl.dataframe)->pl.dataframe:
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
    row_count = {}
    with xlsxwriter.Workbook(f"demo_files/{xlsx_file_name}.xlsx") as f:
        for frame in split_tables_sheet(data):
            sheet = frame["platform"].min()
            if sheet in row_count:
                position = "A" + str(row_count[sheet])
                row_count[sheet] += frame.shape[0] + 2
            else:
                position = "A1"
                row_count[sheet] = frame.shape[0] + 3
            header_format = {
                "font_color" : colors_hex[sheet]["text"],
                "bold":True,
                "bg_color":colors_hex[sheet]["bg"]
            }
            frame.write_excel(f, sheet,
                              position=position,
                              autofit=True,
                              header_format=header_format,
                              hide_gridlines=False)