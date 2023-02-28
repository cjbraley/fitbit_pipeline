from datetime import datetime, timedelta, date
import dotenv
import os
import prefect
from prefect import flow, task
from prefect_shell import ShellOperation

from fitbit_api.api import get_authd_client, intraday_request, get_auth_token, sleep_request
from s3.s3 import upload_to_s3, get_client
from utils.utils import df_to_parquet_buffer
from redshift.redshift import get_redshift_connection, get_copy_query

dotenv.load_dotenv(override=True)  # use .env file

BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
DBT_HOME = os.environ.get('DBT_HOME')
REDSHIFT_CLUSTER_HOST = os.environ.get('REDSHIFT_CLUSTER_HOST')
REDSHIFT_CLUSTER_PORT = os.environ.get('REDSHIFT_CLUSTER_PORT')
REDSHIFT_ADMIN_USER = os.environ.get('TF_VAR_REDSHIFT_ADMIN_USER')
REDSHIFT_PW = os.environ.get('TF_VAR_REDSHIFT_PW')
REDSHIFT_DATABASE_NAME = os.environ.get('TF_VAR_REDSHIFT_DATABASE_NAME')
REDSHIFT_SCHEMA_RAW = os.environ.get('REDSHIFT_SCHEMA_RAW')
REDSHIFT_SCHEMA_ANALYTICS = os.environ.get('REDSHIFT_SCHEMA_ANALYTICS')


intraday_resources = [
    {"name": "heart", "type": "int32"},
    {"name": "steps", "type": "int32"},
    {"name": "distance", "type": "float"},
]


# Never finishes when defined as task
# @task(name="Get Fitbit auth token", description="Get updated auth token for Fitbit API")
def refresh_fitbit_auth_token():
    get_auth_token()


@task(name="Fitbit client", description="Get authorised Fitbit api client")
def get_fitbit_client():
    return get_authd_client()


# Thread lock error if defined as task. To investigate
# @task(name="S3 client", description="Get authorised S3 api client")
def get_s3_client():
    return get_client()


# pickle error if defined as task
# @task(name="Redshift connection", description="Get connection to redshift")
def get_redshift():
    return get_redshift_connection()


@task(name="Intraday - Fetch & Upload", description="Fetch data from Fitbit API and upload to S3", task_run_name="{resource} - Fetch & Upload")
def intraday_fetch_upload(fitbit_client, s3_client, date, resource, datatype):
    df = intraday_request(
        fitbit_client, date, '15min',  resource, datatype)
    parquet = df_to_parquet_buffer(df)
    upload_to_s3(s3_client, parquet, BUCKET_NAME,
                 f"{resource}/{resource}_{date.year}.{date.month:02d}.{date.day:02d}.parquet")
    parquet.close()


@task(name="Sleep - Fetch & Upload", description="Fetch sleep data from Fitbit API and upload to S3")
def sleep_fetch_upload(fitbit_client, s3_client, date):
    df = sleep_request(fitbit_client, date)
    # don't upload if no data
    if df.empty:
        return

    parquet = df_to_parquet_buffer(df)
    upload_to_s3(s3_client, parquet, BUCKET_NAME,
                 f"sleep/sleep_{date.year}.{date.month:02d}.{date.day:02d}.parquet")
    parquet.close()


@task(name="redshift - copy", description="Execute copy commands in Redshift to copy S3 data across. Copy jobs must be idempotent.")
def redshift_copy_from_s3(engine, date):
    # run queries
    with engine.connect() as con:
        # intraday
        for resource in intraday_resources:
            con.execute(get_copy_query(
                resource['name'], 'TRUNC(activity_datetime)', date))

        # sleep
        con.execute(get_copy_query('sleep', 'activity_date', date))


@task()
def run_dtb():
    ShellOperation(
        commands=[
            "cd ${DBT_HOME} && dbt run",
            "cd ${DBT_HOME} && dbt test",

        ],
        # pass env variables.
        env={"DBT_HOME": DBT_HOME,
             "TF_VAR_REDSHIFT_ADMIN_USER": REDSHIFT_ADMIN_USER,
             "TF_VAR_REDSHIFT_PW": REDSHIFT_PW,
             "REDSHIFT_CLUSTER_HOST,": REDSHIFT_CLUSTER_HOST,
             "REDSHIFT_CLUSTER_PORT": REDSHIFT_CLUSTER_PORT,
             "TF_VAR_REDSHIFT_DATABASE_NAME": REDSHIFT_DATABASE_NAME,
             "REDSHIFT_SCHEMA_RAW": REDSHIFT_SCHEMA_RAW,
             "REDSHIFT_SCHEMA_ANALYTICS": REDSHIFT_SCHEMA_ANALYTICS
             }
    ).run()


@flow(name="ingest_fitbit_data", retries=5, retry_delay_seconds=60*30, timeout_seconds=600, log_prints=True)
def ingest_fitbit_data(override_date=None, disable_fitbit_token_refresh=False, disable_dbt=False):

    # get schedule date
    schedule_date = prefect.context.get_run_context().flow_run.dict()[
        "expected_start_time"]
    request_date = schedule_date - timedelta(days=1)

    if override_date:
        request_date = override_date

    print(f"### RUNNING FOR {request_date.date()} ###")

    # refresh auth token
    if not disable_fitbit_token_refresh:
        refresh_fitbit_auth_token()

    # Get fitbit client
    fitbit_client = get_fitbit_client()

    # Get S3 client
    s3_client = get_s3_client()

    # Get data from api + ingest
    # intraday
    for resource in intraday_resources:
        intraday_fetch_upload(fitbit_client, s3_client,
                              request_date, resource['name'], resource['type'])

    # sleep
    sleep_fetch_upload(fitbit_client, s3_client, request_date)

    # Get redshift conn
    redshift_engine = get_redshift()

    # Run copy commands
    redshift_copy_from_s3(redshift_engine, request_date)

    # run dbt with updated data
    if not disable_dbt:
        run_dtb()


if __name__ == "__main__":
    request_date = datetime.today() - timedelta(days=1)
    ingest_fitbit_data(override_date=request_date)
