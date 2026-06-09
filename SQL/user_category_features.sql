DROP TABLE IF EXISTS uc_daily_behavior;

CREATE TABLE uc_daily_behavior AS
SELECT
    user_id,
    item_category,
    date(sample_time) AS action_date,

    SUM(CASE WHEN current_behavior_type = 1 THEN 1 ELSE 0 END) AS uc_pv_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 2 THEN 1 ELSE 0 END) AS uc_fav_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 3 THEN 1 ELSE 0 END) AS uc_cart_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 4 THEN 1 ELSE 0 END) AS uc_buy_cnt_1d,
    COUNT(*) AS uc_total_behavior_1d

FROM behavior_base
GROUP BY user_id, item_category, date(sample_time);

CREATE INDEX IF NOT EXISTS idx_uc_daily
ON uc_daily_behavior(user_id, item_category, action_date);

DROP TABLE IF EXISTS user_category_features;

CREATE TABLE user_category_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.uc_pv_cnt_1d), 0) AS uc_pv_cnt_7d,
    COALESCE(SUM(d.uc_fav_cnt_1d), 0) AS uc_fav_cnt_7d,
    COALESCE(SUM(d.uc_cart_cnt_1d), 0) AS uc_cart_cnt_7d,
    COALESCE(SUM(d.uc_buy_cnt_1d), 0) AS uc_buy_cnt_7d,
    COALESCE(SUM(d.uc_total_behavior_1d), 0) AS uc_total_behavior_7d,

    1.0 * COALESCE(SUM(d.uc_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.uc_pv_cnt_1d), 0), 0) AS uc_buy_rate_7d

FROM behavior_base s
LEFT JOIN uc_daily_behavior d
    ON s.user_id = d.user_id
    AND s.item_category = d.item_category
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;