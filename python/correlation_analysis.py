#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correlation analysis and feature selection
"""

# import libraries
import pandas as pd
import numpy as np
from config import *

def correlation_analysis():
    # load data
    df = pd.read_csv("../data/clean_feature_table.csv")
    
    df["sample_time"] = pd.to_datetime(df["sample_time"])
    
    df = df.sort_values("sample_time").reset_index(drop=True)
    
    n = len(df)
    
    train_end = int(n * TRAIN_RATIO)
    valid_end = int(n * (TRAIN_RATIO + VALID_RATIO))
    
    train_df = df.iloc[:train_end]
    valid_df = df.iloc[train_end:valid_end]
    
    train_valid_df = pd.concat(
        [train_df, valid_df],
        axis=0
    ).reset_index(drop=True)
    
    # keep features only
    drop_cols = [
        "sample_id",
        "user_id",
        "item_id",
        "item_category",
        "sample_time",
        "label"
    ]
    
    X = train_valid_df.drop(columns=drop_cols)
    
    print("Number of features:", X.shape[1])
    
    # correlation matrix
    corr_matrix = X.corr().abs()
    
    # upper triangle
    upper = corr_matrix.where(
        np.triu(
            np.ones(corr_matrix.shape),
            k=1
        ).astype(bool)
    )
    
    # find highly correlated pairs
    high_corr_pairs = []
    
    for column in upper.columns:
    
        high_corr_features = upper.index[
            upper[column] > 0.95
        ].tolist()
    
        for feature in high_corr_features:
    
            high_corr_pairs.append(
                {
                    "feature_1": feature,
                    "feature_2": column,
                    "correlation": upper.loc[feature, column]
                }
            )
    
    corr_df = pd.DataFrame(high_corr_pairs)
    
    print("\nHighly correlated pairs")
    print(corr_df)
    
    
    corr_df.to_csv(
        "../data/high_correlation_pairs.csv",
        index=False
    )
    
    # suggested features to drop
    drop_features = [
        column
        for column in upper.columns
        if any(upper[column] > 0.95)
    ]
    
    print("\nSuggested features to drop")
    print(drop_features)
    
    print("\nNumber of features to remove:", len(drop_features))
    
    pd.DataFrame(
        {
            "drop_feature": drop_features
        }
    ).to_csv(
        "../data/high_correlation_drop_features.csv",
        index=False
    )
    
    print("\nCorrelation analysis completed.")
    
    # %%
    from final_model import train_final_model
    
    drop_features = [
        "user_total_behavior_7d",
        "item_total_behavior_7d",
        "item_unique_user_7d",
        "cate_fav_cnt_7d",
        "cate_cart_cnt_7d",
        "cate_total_behavior_7d",
        "ui_total_behavior_7d",
        "ui_has_fav_7d",
        "uc_total_behavior_7d",
        "ui_has_buy_7d",
        "ui_buy_cnt_7d",
        "item_night_buy_cnt_7d",
        "item_weekend_buy_cnt_7d",
        "cate_night_buy_cnt_7d",
        "cate_weekend_buy_cnt_7d"
    ]
    
    train_final_model(
        drop_features=drop_features,
        save_prefix="corr_selection"
    )

if __name__ == "__main__":
    train_final_model()