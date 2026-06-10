#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

import pandas as pd
import sqlite3

# 创建数据库
conn = sqlite3.connect("behavior.db")
cursor = conn.cursor()

# 导入csv
df = pd.read_csv("../data/data_min.csv")

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
DROP TABLE IF EXISTS behavior_base
""")

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

# 创建索引
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_user_time
ON behavior_base(user_id,sample_time)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_item_time
ON behavior_base(item_id,sample_time)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_cate_time
ON behavior_base(item_category,sample_time)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_ui_time
ON behavior_base(user_id,item_id,sample_time)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_uc_time
ON behavior_base(user_id,item_category,sample_time)
""")

conn.commit()

print("Database Created Successfully")

# %%
# 执行所有sql脚本
sql_files = [
    "../sql/user_features.sql",
    "../sql/item_features.sql",
    "../sql/category_features.sql",
    "../sql/user_item_features.sql",
    "../sql/user_category_features.sql",
    "../sql/time_features.sql",
    "../sql/user_time_features.sql",
    "../sql/item_time_features.sql",
    "../sql/category_time_features.sql",
    "../sql/time_gap_features.sql",
    "../sql/label.sql",
    "../sql/merge_features.sql"
]

for file in sql_files:
    print(f"Running {file}")

    with open(file, "r") as f:
        cursor.executescript(f.read())

    conn.commit()

print("All SQL scripts completed.")

conn.close()