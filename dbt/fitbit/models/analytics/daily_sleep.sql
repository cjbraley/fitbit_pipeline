{{ config(materialized="table") }}

WITH 
sleep1 AS (
    SELECT
        *,
        deep_sleep_minutes + rem_sleep_minutes + light_sleep_minutes AS asleep_minutes,
        deep_sleep_minutes + rem_sleep_minutes + light_sleep_minutes + awake_minutes AS in_bed_minutes
    FROM {{ ref("staging_sleep") }}
),
sleep2 AS (
    SELECT
        *,
        LEAST(ROUND((CAST(asleep_minutes AS FLOAT) / CAST(in_bed_minutes AS FLOAT)) * 100), 100) AS score_sleep_efficiency,
        LEAST(ROUND(CAST(asleep_minutes AS FLOAT) / CAST(sleep_minutes_goal AS FLOAT) * 100), 100) AS score_sleep_amount,
        LEAST(ROUND((CAST(rem_sleep_minutes AS FLOAT) / CAST(asleep_minutes AS FLOAT)) / 0.20 * 100), 100) AS score_rem_percent, -- target is 20%
        LEAST(ROUND((CAST(deep_sleep_minutes AS FLOAT) / CAST(asleep_minutes AS FLOAT)) / 0.16  * 100), 100) AS score_deep_percent -- target is 16%
    FROM sleep1
)

SELECT
    *,
    ROUND(score_sleep_amount * 0.5 + score_rem_percent * 0.125 + score_deep_percent * 0.125 + score_sleep_efficiency * 0.25) AS score_sleep_total
FROM sleep2
