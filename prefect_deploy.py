""" Run this to create and apply deployments of included flows"""
from prefect_pipeline import ingest_fitbit_data
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule


# Set Schedule
# Needs to run after wakeup time to capture sleep data
schedule_daily = CronSchedule(cron="0 10 * * *", timezone="Australia/Sydney")

# Define deployment
ingest_deployment = Deployment.build_from_flow(
    flow=ingest_fitbit_data,
    name="fitbit_daily",
    work_queue_name="default_worker_pool",
    schedule=schedule_daily,
    infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}}
)


if __name__ == "__main__":
    ingest_deployment.apply()
