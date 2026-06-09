DROP TABLE IF EXISTS user_time_daily_behavior;

CREATE TABLE user_time_daily_behavior AS
SELECT
    user_id,
    date(sample_time) AS action_date,

    SUM(
        CASE
            WHEN CAST(strftime('%H', sample_time) AS INTEGER) >= 22
              OR CAST(strftime('%H', sample_time) AS INTEGER) <= 6
            THEN 1 ELSE 0
        END
    ) AS user_night_behavior_cnt_1d,

    SUM(
        CASE
            WHEN CAST(strftime('%w', sample_time) AS INTEGER) IN (0,6)
            THEN 1 ELSE 0
        END
    ) AS user_weekend_behavior_cnt_1d,

    COUNT(*) AS user_total_behavior_1d

FROM behavior_base
GROUP BY user_id, date(sample_time);


CREATE INDEX IF NOT EXISTS idx_user_time_daily
ON user_time_daily_behavior(user_id, action_date);


DROP TABLE IF EXISTS user_time_features;

CREATE TABLE user_time_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.user_night_behavior_cnt_1d), 0) AS user_night_behavior_cnt_7d,
    COALESCE(SUM(d.user_weekend_behavior_cnt_1d), 0) AS user_weekend_behavior_cnt_7d,

    1.0 * COALESCE(SUM(d.user_night_behavior_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.user_total_behavior_1d), 0), 0) AS user_night_ratio_7d,

    1.0 * COALESCE(SUM(d.user_weekend_behavior_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.user_total_behavior_1d), 0), 0) AS user_weekend_ratio_7d

FROM behavior_base s
LEFT JOIN user_time_daily_behavior d
    ON s.user_id = d.user_id
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;