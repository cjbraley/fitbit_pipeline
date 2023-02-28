{{ config(materialized=("view" if target.name == 'dev' else "ephemeral")) }}

WITH steps AS (
    SELECT
        activity_datetime,
        value AS steps
    FROM {{ source("raw_data","steps")}}
),
distance AS (
    SELECT
        activity_datetime,
        value * 1000 AS distance_meters
    FROM {{ source("raw_data","distance")}}
),
heartbeat AS (
    SELECT
        activity_datetime,
        value AS heartbeat
    FROM {{ source("raw_data","heart")}}
)

SELECT
    cast(s.activity_datetime AS TIMESTAMP) AS activity_datetime,
    cast(steps AS INTEGER) AS steps,
    cast(ROUND(distance_meters) AS INTEGER) AS distance_meters,
    cast(heartbeat AS INTEGER) AS heartbeat
FROM steps s
INNER JOIN distance d ON s.activity_datetime = d.activity_datetime
INNER JOIN heartbeat h ON s.activity_datetime = h.activity_datetime