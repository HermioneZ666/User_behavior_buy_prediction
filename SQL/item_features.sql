DROP TABLE IF EXISTS item_daily_behavior;

CREATE TABLE item_daily_behavior AS
SELECT
    item_id,
    date(sample_time) AS action_date,

    SUM(CASE WHEN current_behavior_type = 1 THEN 1 ELSE 0 END) AS item_pv_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 2 THEN 1 ELSE 0 END) AS item_fav_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 3 THEN 1 ELSE 0 END) AS item_cart_cnt_1d,
    SUM(CASE WHEN current_behavior_type = 4 THEN 1 ELSE 0 END) AS item_buy_cnt_1d,
    COUNT(*) AS item_total_behavior_1d,
    COUNT(DISTINCT user_id) AS item_unique_user_1d

FROM behavior_base
GROUP BY item_id, date(sample_time);

CREATE INDEX IF NOT EXISTS idx_item_daily
ON item_daily_behavior(item_id, action_date);

DROP TABLE IF EXISTS item_features;

CREATE TABLE item_features AS
SELECT
    s.sample_id,

    COALESCE(SUM(d.item_pv_cnt_1d), 0) AS item_pv_cnt_7d,
    COALESCE(SUM(d.item_fav_cnt_1d), 0) AS item_fav_cnt_7d,
    COALESCE(SUM(d.item_cart_cnt_1d), 0) AS item_cart_cnt_7d,
    COALESCE(SUM(d.item_buy_cnt_1d), 0) AS item_buy_cnt_7d,
    COALESCE(SUM(d.item_total_behavior_1d), 0) AS item_total_behavior_7d,
    COALESCE(SUM(d.item_unique_user_1d), 0) AS item_unique_user_7d,

    1.0 * COALESCE(SUM(d.item_buy_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.item_pv_cnt_1d), 0), 0) AS item_buy_rate_7d,

    1.0 * COALESCE(SUM(d.item_cart_cnt_1d), 0)
        / NULLIF(COALESCE(SUM(d.item_pv_cnt_1d), 0), 0) AS item_cart_rate_7d

FROM behavior_base s
LEFT JOIN item_daily_behavior d
    ON s.item_id = d.item_id
    AND d.action_date >= date(s.sample_time, '-7 days')
    AND d.action_date < date(s.sample_time)

GROUP BY s.sample_id;