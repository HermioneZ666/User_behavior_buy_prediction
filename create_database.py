#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

import pandas as pd
import sqlite3

# 创建数据库
conn = sqlite3.connect("behavior.db")

# 导入csv
df = pd.read_csv("data/data_min.csv")

# 写入数据库，user_behavior_raw 为原始行为表
df.to_sql(
    "user_behavior_raw",
    conn,
    if_exists="replace",
    index=False
)

print("Import Success")

# %%
# 创建标准化基础表 behavior_base
conn.execute("""
CREATE TABLE behavior_base AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY user_id, item_id, time, behavior_type
    ) AS sample_id,
    user_id,
    item_id,
    item_category,
    behavior_type AS current_behavior_type,
    datetime(time || ':00:00') AS sample_time
FROM user_behavior_raw;
""")

conn.commit()

print("Database Created Successfully")