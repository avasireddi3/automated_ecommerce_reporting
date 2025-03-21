import xlsxwriter
import polars as pl
from src.config import xlsx_file_name, colors_hex
from src.utils.validators import check_path

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

def write_excel(data:pl.dataframe,report_path:str="report_files/")->None:
    """write data to xlsx file"""
    row_count = {}
    check_path()
    with xlsxwriter.Workbook(report_path+"{xlsx_file_name}.xlsx",
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