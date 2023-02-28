{{ config(materialized=("view" if target.name == 'dev' else "ephemeral")) }}

WITH sleep AS (
    SELECT
        *
    FROM {{ source("raw_data","sleep")}}
)

SELECT
    activity_date,
    CAST(startTime AS TIME) AS sleep_start_time,
    CAST(endTime AS TIME) AS sleep_end_time,
    cast(bedtime AS TIME) as bed_time_goal,
    minDuration AS sleep_minutes_goal,
    minutesToFallAsleep AS minutes_to_fall_asleep,
    deep AS deep_sleep_minutes,
    rem AS rem_sleep_minutes,
    light AS light_sleep_minutes,
    awake AS awake_minutes
FROM sleep