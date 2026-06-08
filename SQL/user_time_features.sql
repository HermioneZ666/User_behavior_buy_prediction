CREATE TABLE user_time_features AS
SELECT
    s.sample_id,

    SUM(
        CASE
            WHEN CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    ) AS user_night_behavior_cnt_7d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    ) AS user_weekend_behavior_cnt_7d,

    COUNT(
        DISTINCT CAST(strftime('%H', b.sample_time) AS INTEGER)
    ) AS user_active_hour_cnt_7d,

    1.0 *
    SUM(
        CASE
            WHEN CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    )
    / NULLIF(COUNT(b.sample_id),0)
    AS user_night_ratio_7d,

    1.0 *
    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    )
    / NULLIF(COUNT(b.sample_id),0)
    AS user_weekend_ratio_7d

FROM behavior_base s

LEFT JOIN behavior_base b
ON s.user_id = b.user_id
AND b.sample_time >= datetime(s.sample_time,'-7 days')
AND b.sample_time < s.sample_time

GROUP BY s.sample_id;