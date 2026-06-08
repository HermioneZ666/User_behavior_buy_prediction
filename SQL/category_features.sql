#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

CREATE TABLE category_features AS
SELECT
    s.sample_id,

    SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END) AS cate_pv_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 2 THEN 1 ELSE 0 END) AS cate_fav_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END) AS cate_cart_cnt_7d,
    SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END) AS cate_buy_cnt_7d,
    COUNT(b.sample_id) AS cate_total_behavior_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS cate_buy_rate_7d,

    1.0 * SUM(CASE WHEN b.current_behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN b.current_behavior_type = 1 THEN 1 ELSE 0 END), 0) AS cate_cart_rate_7d

FROM behavior_base s
LEFT JOIN behavior_base b
    ON s.item_category = b.item_category
    AND b.sample_time >= datetime(s.sample_time, '-7 days')
    AND b.sample_time < s.sample_time
GROUP BY s.sample_id;