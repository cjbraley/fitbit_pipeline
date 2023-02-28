from datetime import datetime, timedelta
from prefect import flow, task
from sqlalchemy import create_engine
import os
import dotenv
import pandas as pd
from prefect_shell import ShellOperation

dotenv.load_dotenv()  # use .env file

BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
REDSHIFT_CLUSTER_HOST = os.environ.get('REDSHIFT_CLUSTER_HOST')
REDSHIFT_CLUSTER_PORT = os.environ.get('REDSHIFT_CLUSTER_PORT')
REDSHIFT_SCHEMA_RAW = os.environ.get('REDSHIFT_SCHEMA_RAW')
REDSHIFT_ADMIN_USER = os.environ.get('TF_VAR_REDSHIFT_ADMIN_USER')
REDSHIFT_PW = os.environ.get('TF_VAR_REDSHIFT_PW')
REDSHIFT_DATABASE_NAME = os.environ.get('TF_VAR_REDSHIFT_DATABASE_NAME')


schema_query = f"CREATE SCHEMA IF NOT EXISTS \"{REDSHIFT_SCHEMA_RAW}\";"


def get_redshift_connection():
    # form connection string
    connection_string = f'postgresql://{REDSHIFT_ADMIN_USER}:{REDSHIFT_PW}@{REDSHIFT_CLUSTER_HOST}:{REDSHIFT_CLUSTER_PORT}/{REDSHIFT_DATABASE_NAME}'
    # connect to db
    return create_engine(connection_string)


def get_raw_schema_query():
    return f"CREATE SCHEMA IF NOT EXISTS \"{REDSHIFT_SCHEMA_RAW}\";"


def get_intraday_create_table_query(name, valueType):
    return f"""
        CREATE TABLE IF NOT EXISTS "{REDSHIFT_SCHEMA_RAW}"."{name}"
        (
            activity_datetime TIMESTAMP NULL, 
            value {valueType} NULL
        ) ENCODE AUTO;
        """


def get_sleep_create_table_query():
    return f"""
    CREATE TABLE IF NOT EXISTS "{REDSHIFT_SCHEMA_RAW}"."sleep"
    (
        "deep" INTEGER,
        "light" INTEGER,
        "rem" INTEGER,
        "awake" INTEGER,
        "activity_date" DATE, 
        "startTime" TIMESTAMP,
        "endTime" TIMESTAMP,
        "minutesToFallAsleep" INTEGER,
        "bedtime" VARCHAR(256),
        "minDuration" INTEGER
    )
    DISTSTYLE EVEN
    ;
    """


def get_copy_query(resource, where, date):
    return f"""
        DELETE FROM "{REDSHIFT_SCHEMA_RAW}"."{resource}" WHERE {where} = '{date.date()}';
        COPY "{REDSHIFT_SCHEMA_RAW}"."{resource}"
        FROM 's3://{BUCKET_NAME}/{resource}/{resource}_{date.year}.{date.month:02d}.{date.day:02d}.parquet'
        access_key_id  '{AWS_ACCESS_KEY}'
        secret_access_key '{AWS_SECRET_KEY}'
        FORMAT AS PARQUET
    """


if __name__ == "__main__":
    pass
