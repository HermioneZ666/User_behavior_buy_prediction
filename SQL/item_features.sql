#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

CREATE TABLE item_features AS
SELECT
    s.sample_id,

    SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END) AS item_pv_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 2 THEN 1 ELSE 0 END) AS item_fav_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END) AS item_cart_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END) AS item_buy_cnt_7d,
    COUNT(b.sample_id) AS item_total_behavior_7d,
    COUNT(DISTINCT b.user_id) AS item_unique_user_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS item_buy_rate_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS item_cart_rate_7d

FROM behavior_base s
LEFT JOIN behavior_base b
    ON s.item_id = b.item_id
    AND b.sample_time >= datetime(s.sample_time, '-7 days')
    AND b.sample_time < s.sample_time
GROUP BY s.sample_id;
