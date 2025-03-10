import polars as pl
import xlsxwriter
from clean_data import yield_tables

def write_db(data:pl.dataframe):
    data.write_database(table_name="test_listings",connection="sqlite:////home/avasireddi3/projects/saroj_analytics/test.db",
                        if_table_exists="append")

def write_excel(data:pl.dataframe)->None:
    row_count = {}
    with xlsxwriter.Workbook("test_report.xlsx") as f:
        for frame in yield_tables(data):
            print(frame.shape)
            sheet = frame["platform"].min()
            print(sheet)
            if sheet in row_count:
                position = "A" + str(row_count[sheet])
                row_count[sheet] += frame.shape[0] + 2
            else:
                position = "A1"
                row_count[sheet] = frame.shape[0] + 3
            frame.write_excel(f, sheet, position=position, table_style="Table Style Medium 4")
            print(row_count)