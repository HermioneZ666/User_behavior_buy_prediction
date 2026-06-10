#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

import sqlite3
import pandas as pd
import numpy as np

# load data
conn = sqlite3.connect("../behavior.db")

df = pd.read_sql(
    """
    SELECT *
    FROM feature_table
    """,
    conn
)

print("Data loaded successfully.")
print("Shape:", df.shape)

# basic information
print("\nBasic information")
print(df.info())

print("\nFirst 5 rows")
print(df.head(5))

# label distribution
print("\nLabel distribution")
print(df["label"].value_counts(dropna=False))

print("\nLabel distribution ratio")
print(df["label"].value_counts(normalize=True, dropna=False))

# duplicate sample check
print("\nDuplicate sample_id check")
duplicate_cnt = df["sample_id"].duplicated().sum()
print("Duplicate sample_id count:", duplicate_cnt)

# missing value check
print("\nMissing values")

missing_cnt = df.isnull().sum()
missing_rate = df.isnull().mean() * 100
missing_summary = pd.DataFrame({
    "missing_count": missing_cnt,
    "missing_rate_percent": missing_rate
})

missing_summary = (
    missing_summary[missing_summary["missing_count"] > 0]
    .sort_values(
        by="missing_count",
        ascending=False
    )
)

print(missing_summary)

# missing value handling
gap_cols = [
    "user_last_action_gap_hour",
    "ui_last_action_gap_hour",
    "uc_last_action_gap_hour"
]

for col in gap_cols:
    if col in df.columns:
        max_gap = df[col].max(skipna=True)

        if pd.notnull(max_gap):
            df[col] = df[col].fillna(max_gap)
        else:
            df[col] = df[col].fillna(9999)

df = df.fillna(0)

print("\nMissing values after filling")
print("Total missing values:", df.isnull().sum().sum())

# ratio columns check
ratio_cols = [
    col
    for col in df.columns
    if ("rate" in col.lower())
    or ("ratio" in col.lower())
]

print("\nRatio / rate columns summary")
print(df[ratio_cols].describe())

ratio_abnormal = {}
for col in ratio_cols:
    abnormal_cnt = (
        (df[col] < 0)
        | (df[col] > 1)
    ).sum()

    if abnormal_cnt > 0:
        ratio_abnormal[col] = abnormal_cnt

print("\nRatio columns outside [0,1]")
print(ratio_abnormal)

# time feature check
time_cols = [
    col
    for col in [
        "hour",
        "weekday",
        "is_weekend",
        "is_night"
    ]
    if col in df.columns
]

print("\nTime feature summary")
print(df[time_cols].describe())

# convert label type
df["label"] = df["label"].astype(int)

# save cleaned data
output_path = "../data/clean_feature_table.csv"

df.to_csv(
    output_path,
    index=False
)

print("\nCleaned feature table saved to")
print(output_path)

# close database connection
conn.close()

print("\nData preprocessing completed.")