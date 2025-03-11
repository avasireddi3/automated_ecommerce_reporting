import polars as pl
import polars_ds as pds


def filter_clean()->pl.dataframe:
    data = pl.read_csv("demo_files/test.csv")
    data = data.filter(
        pl.col("brand").is_not_null(),
        pl.col("brand")!="BUNDLE"
    )
    data = data.with_columns(
        product_name = pl.col("name").str.strip_prefix(pl.col("brand")),
        ppu = pl.col("price")/pl.col("unit"),
        discount_pct = (((pl.col("mrp")-pl.col("price"))*100)/pl.col("mrp")).round(2)
    )
    data = data.with_columns(
        similarity = pds.str_fuzz("search_term","product_name")
    )
    data = data.filter(
        pl.col("similarity")>0.45
    )
    return data



def split_tables_report(data:pl.dataframe)->pl.dataframe:
    dataframes = data.select(["platform",
                   "timestamp",
                   "search_term",
                   "brand",
                   "product_name",
                   "mrp",
                   "price",
                   "unit",
                   "ppu",
                   "discount_pct"]).partition_by(["platform","search_term"])
    for frame in dataframes:
        yield frame

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





