{{ config(materialized="table") }}

WITH intraday AS (
    SELECT
        activity_datetime,
        steps,
        distance_meters,
        heartbeat
    FROM {{ ref("staging_intraday")}}
)


SELECT
    TRUNC(activity_datetime) AS activity_date,
    activity_datetime,
    steps,
    distance_meters,
    heartbeat
FROM intraday
