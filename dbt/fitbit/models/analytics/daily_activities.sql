{{ config(materialized="table") }}

WITH intraday AS (
    SELECT
        TRUNC(activity_datetime) AS activity_date,
        steps,
        distance_meters,
        heartbeat
    FROM {{ ref("staging_intraday")}}
)


SELECT
    activity_date,
    SUM(steps) AS total_steps,
    SUM(distance_meters) AS total_distance_meters,
    MAX(heartbeat) AS max_heartbeat
FROM intraday
GROUP BY activity_date
