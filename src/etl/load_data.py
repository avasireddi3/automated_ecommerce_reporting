import polars as pl
import xlsxwriter

colors = {
            "zepto":{"text":"#f73563",
                     "bg":"#390067"},
            "instamart":{"text":"#f7f7f7",
                         "bg":"#f74f00"},
            "blinkit":{"text":"#2f8215",
                       "bg":"#f0c544"}
        }

def write_db(data:pl.dataframe):
    data.write_database(table_name="test_listings",connection="sqlite:////home/avasireddi3/projects/saroj_analytics/test.db",
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
    with xlsxwriter.Workbook("demo_files/test_report.xlsx") as f:
        for frame in split_tables_sheet(data):
            sheet = frame["platform"].min()
            if sheet in row_count:
                position = "A" + str(row_count[sheet])
                row_count[sheet] += frame.shape[0] + 2
            else:
                position = "A1"
                row_count[sheet] = frame.shape[0] + 3
            header_format = {
                "font_color" : colors[sheet]["text"],
                "bold":True,
                "bg_color":colors[sheet]["bg"]
            }
            frame.write_excel(f, sheet,
                              position=position,
                              autofit=True,
                              header_format=header_format,
                              hide_gridlines=False)