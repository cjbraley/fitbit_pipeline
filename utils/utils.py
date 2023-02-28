from io import BytesIO
import pandas as pd


def df_to_parquet_buffer(df):

    # convert to bytes
    bytes_data = df.to_parquet()
    # init buffer
    buffer = BytesIO(bytes_data)

    return buffer
