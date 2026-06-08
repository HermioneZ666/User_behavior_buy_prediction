CREATE TABLE item_time_features AS
SELECT
    s.sample_id,

    SUM(
        CASE
            WHEN CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    ) AS item_night_behavior_cnt_7d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    ) AS item_weekend_behavior_cnt_7d,

    SUM(
        CASE
            WHEN (
                CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
                OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            )
            AND b.current_behavior_type = 4
            THEN 1 ELSE 0
        END
    ) AS item_night_buy_cnt_7d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            AND b.current_behavior_type = 4
            THEN 1 ELSE 0
        END
    ) AS item_weekend_buy_cnt_7d,

    1.0 *
    SUM(
        CASE
            WHEN CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    )
    / NULLIF(COUNT(b.sample_id),0)
    AS item_night_ratio_7d,

    1.0 *
    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    )
    / NULLIF(COUNT(b.sample_id),0)
    AS item_weekend_ratio_7d,

    1.0 *
    SUM(
        CASE
            WHEN (
                CAST(strftime('%H', b.sample_time) AS INTEGER) >= 22
                OR CAST(strftime('%H', b.sample_time) AS INTEGER) <= 6
            )
            AND b.current_behavior_type = 4
            THEN 1 ELSE 0
        END
    )
    / NULLIF(
        SUM(
            CASE
                WHEN b.current_behavior_type = 4
                THEN 1 ELSE 0
            END
        ),0
    )
    AS item_night_buy_ratio_7d,

    1.0 *
    SUM(
        CASE
            WHEN CAST(strftime('%w', b.sample_time) AS INTEGER) IN (0,6)
            AND b.current_behavior_type = 4
            THEN 1 ELSE 0
        END
    )
    / NULLIF(
        SUM(
            CASE
                WHEN b.current_behavior_type = 4
                THEN 1 ELSE 0
            END
        ),0
    )
    AS item_weekend_buy_ratio_7d

FROM behavior_base s

LEFT JOIN behavior_base b
ON s.item_id = b.item_id
AND b.sample_time >= datetime(s.sample_time,'-7 days')
AND b.sample_time < s.sample_time

GROUP BY s.sample_id;