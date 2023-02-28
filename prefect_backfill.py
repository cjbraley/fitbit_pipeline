### USE THIS SCRIPT TO BACKFILL PAST DATES ###
""" Unlike Airflow, Prefect currently does catch up old dates without intervention """
from datetime import datetime, timedelta
from prefect_pipeline import ingest_fitbit_data, run_dtb, refresh_fitbit_auth_token
from prefect import flow


@flow(name="backfill", retries=0, log_prints=True)
def backfill(start_date, end_date):
    refresh_fitbit_auth_token()

    current_date = start_date
    while current_date <= end_date:
        ingest_fitbit_data(override_date=current_date,
                           disable_fitbit_token_refresh=True, disable_dbt=True)
        current_date += timedelta(days=1)

    # run with dbt once at the end
    run_dtb()


if __name__ == "__main__":
    # set backfill start & end
    start = datetime(2023, 2, 24)
    end = datetime(2023, 2, 26)
    backfill(start, end)
