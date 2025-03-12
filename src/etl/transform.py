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











