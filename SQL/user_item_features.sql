DROP TABLE IF EXISTS ui_daily_behavior;

CREATE TABLE ui_daily_behavior AS
SELECT
    user_id,
    item_id,
    date(sample_time) AS action_date,

    SUM(CASE WHEN current_behavior_type = 1 THEN 1 ELSE 0 END) AS ui_pv_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 2 THEN 1 ELSE 0 END) AS ui_fav_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 3 THEN 1 ELSE 0 END) AS ui_cart_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 4 THEN 1 ELSE 0 END) AS ui_buy_cnt_1d,
    COUNT(*) AS ui_total_behavior_1d

FROM behavior_base
GROUP BY user_id, item_id, date(sample_time);

CREATE INDEX IF NOT EXISTS idx_ui_daily
ON ui_daily_behavior(user_id, item_id, action_date);

DROP TABLE IF EXISTS user_item_features;

CREATE TABLE user_item_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.ui_pv_cnt_1d), 0) AS ui_pv_cnt_7d,
    COALESCE(SUM(d.ui_fav_cnt_1d), 0) AS ui_fav_cnt_7d,
    COALESCE(SUM(d.ui_cart_cnt_1d), 0) AS ui_cart_cnt_7d,
    COALESCE(SUM(d.ui_buy_cnt_1d), 0) AS ui_buy_cnt_7d,
    COALESCE(SUM(d.ui_total_behavior_1d), 0) AS ui_total_behavior_7d,

    1.0 * COALESCE(SUM(d.ui_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.ui_pv_cnt_1d), 0), 0) AS ui_buy_rate_7d,

    1.0 * COALESCE(SUM(d.ui_cart_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.ui_pv_cnt_1d), 0), 0) AS ui_cart_rate_7d,

    CASE WHEN COALESCE(SUM(d.ui_fav_cnt_1d), 0) > 0 THEN 1 ELSE 0 END AS ui_has_fav_7d,
    CASE WHEN COALESCE(SUM(d.ui_cart_cnt_1d), 0) > 0 THEN 1 ELSE 0 END AS ui_has_cart_7d,
    CASE WHEN COALESCE(SUM(d.ui_buy_cnt_1d), 0) > 0 THEN 1 ELSE 0 END AS ui_has_buy_7d

FROM behavior_base s
LEFT JOIN ui_daily_behavior d
    ON s.user_id = d.user_id
    AND s.item_id = d.item_id
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;