#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

CREATE TABLE user_item_features AS
SELECT
    s.sample_id,

    SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END) AS ui_pv_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 2 THEN 1 ELSE 0 END) AS ui_fav_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END) AS ui_cart_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END) AS ui_buy_cnt_7d,
    COUNT(b.sample_id) AS ui_total_behavior_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS ui_buy_rate_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS ui_cart_rate_7d,

    CASE WHEN SUM(CASE WHEN b.current_behavior_type = 2 THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END AS ui_has_fav_7d,
    CASE WHEN SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END AS ui_has_cart_7d,
    CASE WHEN SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END AS ui_has_buy_7d

FROM behavior_base s
LEFT JOIN behavior_base b
    ON s.user_id = b.user_id
    AND s.item_id = b.item_id
    AND b.sample_time >= datetime(s.sample_time, '-7 days')
    AND b.sample_time < s.sample_time
GROUP BY s.sample_id;