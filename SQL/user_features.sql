DROP TABLE IF EXISTS user_daily_behavior;

CREATE TABLE user_daily_behavior AS
SELECT
    user_id,
    date(sample_time) AS action_date,

    SUM(CASE WHEN current_behavior_type = 1 THEN 1 ELSE 0 END) AS user_pv_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 2 THEN 1 ELSE 0 END) AS user_fav_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 3 THEN 1 ELSE 0 END) AS user_cart_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 4 THEN 1 ELSE 0 END) AS user_buy_cnt_1d,
    COUNT(*) AS user_total_behavior_1d

FROM behavior_base
GROUP BY user_id, date(sample_time);


CREATE INDEX IF NOT EXISTS idx_user_daily
ON user_daily_behavior(user_id, action_date);


DROP TABLE IF EXISTS user_features;

CREATE TABLE user_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.user_pv_cnt_1d), 0) AS user_pv_cnt_7d,
    COALESCE(SUM(d.user_fav_cnt_1d), 0) AS user_fav_cnt_7d,
    COALESCE(SUM(d.user_cart_cnt_1d), 0) AS user_cart_cnt_7d,
    COALESCE(SUM(d.user_buy_cnt_1d), 0) AS user_buy_cnt_7d,
    COALESCE(SUM(d.user_total_behavior_1d), 0) AS user_total_behavior_7d,

    COUNT(DISTINCT d.action_date) AS user_active_days_7d,

    1.0 * COALESCE(SUM(d.user_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.user_pv_cnt_1d), 0), 0) AS user_buy_rate_7d,

    1.0 * COALESCE(SUM(d.user_cart_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.user_pv_cnt_1d), 0), 0) AS user_cart_rate_7d,

    1.0 * COALESCE(SUM(d.user_fav_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.user_pv_cnt_1d), 0), 0) AS user_fav_rate_7d

FROM behavior_base s
LEFT JOIN user_daily_behavior d
    ON s.user_id = d.user_id
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;