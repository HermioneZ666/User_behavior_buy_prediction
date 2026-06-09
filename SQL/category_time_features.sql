DROP TABLE IF EXISTS category_time_daily_behavior;

CREATE TABLE category_time_daily_behavior AS
SELECT
    item_category,
    date(sample_time) AS action_date,

    SUM(
        CASE
            WHEN CAST(strftime('%H', sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    ) AS cate_night_behavior_cnt_1d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    ) AS cate_weekend_behavior_cnt_1d,

    SUM(
        CASE
            WHEN (
                CAST(strftime('%H', sample_time) AS INTEGER) >= 22
                OR CAST(strftime('%H', sample_time) AS INTEGER) <= 6
            )
            AND current_behavior_type = 4
            THEN 1 ELSE 0
        END
    ) AS cate_night_buy_cnt_1d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', sample_time) AS INTEGER) IN (0,6)
             AND current_behavior_type = 4
            THEN 1 ELSE 0
        END
    ) AS cate_weekend_buy_cnt_1d,

    SUM(CASE WHEN current_behavior_type = 4 THEN 1 ELSE 0 END) AS cate_buy_cnt_1d,

    COUNT(*) AS cate_total_behavior_1d

FROM behavior_base
GROUP BY item_category, date(sample_time);


CREATE INDEX IF NOT EXISTS idx_category_time_daily
ON category_time_daily_behavior(item_category, action_date);


DROP TABLE IF EXISTS category_time_features;

CREATE TABLE category_time_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.cate_night_behavior_cnt_1d), 0) AS cate_night_behavior_cnt_7d,
    COALESCE(SUM(d.cate_weekend_behavior_cnt_1d), 0) AS cate_weekend_behavior_cnt_7d,
    COALESCE(SUM(d.cate_night_buy_cnt_1d), 0) AS cate_night_buy_cnt_7d,
    COALESCE(SUM(d.cate_weekend_buy_cnt_1d), 0) AS cate_weekend_buy_cnt_7d,

    1.0 * COALESCE(SUM(d.cate_night_behavior_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.cate_total_behavior_1d), 0), 0) AS cate_night_ratio_7d,

    1.0 * COALESCE(SUM(d.cate_weekend_behavior_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.cate_total_behavior_1d), 0), 0) AS cate_weekend_ratio_7d,

    1.0 * COALESCE(SUM(d.cate_night_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.cate_buy_cnt_1d), 0), 0) AS cate_night_buy_ratio_7d,

    1.0 * COALESCE(SUM(d.cate_weekend_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.cate_buy_cnt_1d), 0), 0) AS cate_weekend_buy_ratio_7d

FROM behavior_base s
LEFT JOIN category_time_daily_behavior d
    ON s.item_category = d.item_category
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;