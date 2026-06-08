CREATE TABLE time_features AS
SELECT
    sample_id,
    CAST(strftime('%H', sample_time) AS INTEGER) AS hour,
    CAST(strftime('%w', sample_time) AS INTEGER) AS weekday,
    CASE WHEN CAST(strftime('%w', sample_time) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend,
    CASE
        WHEN CAST(strftime('%H', sample_time) AS INTEGER) >= 22
          OR CAST(strftime('%H', sample_time) AS INTEGER) <= 6
        THEN 1 ELSE 0
    END AS is_night
FROM behavior_base;