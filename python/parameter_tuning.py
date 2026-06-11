#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter tuning for baseline models using sampled data
"""

# import libraries
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
)

from xgboost import XGBClassifier
from config import *

# load data
df = pd.read_csv("../data/clean_feature_table.csv")

print("Original shape:", df.shape)


# sample data for parameter tuning
df = df.sample(
    n=SAMPLE_SIZE,
    random_state=42
)

print("Sample shape:", df.shape)

# time split
df["sample_time"] = pd.to_datetime(df["sample_time"])

df = df.sort_values("sample_time").reset_index(drop=True)

n = len(df)

train_end = int(n * TRAIN_RATIO)
valid_end = int(n * (TRAIN_RATIO + VALID_RATIO))

train_df = df.iloc[:train_end]
valid_df = df.iloc[train_end:valid_end]
test_df = df.iloc[valid_end:]

# features and labels
drop_cols = [
    "sample_id",
    "user_id",
    "item_id",
    "item_category",
    "sample_time",
    "label"
]

X_train = train_df.drop(columns=drop_cols)
y_train = train_df["label"]

X_valid = valid_df.drop(columns=drop_cols)
y_valid = valid_df["label"]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df["label"]


# evaluation function
def get_metrics(model_name, y_true, y_prob):
    y_pred = (y_prob >= 0.5).astype(int)

    return {
        "model": model_name,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob),
        "pr_auc": average_precision_score(y_true, y_prob)
    }


# Logistic Regression tuning
print("\nStart Logistic Regression tuning")

lr_results = []

for C in LR_C_LIST:
    print(f"\nTraining Logistic Regression with C={C}")

    lr_params = LR_PARAMS.copy()
    lr_params["C"] = C
    lr_params["verbose"] = 0

    lr_model = LogisticRegression(**lr_params)

    lr_model.fit(X_train, y_train)

    valid_prob = lr_model.predict_proba(X_valid)[:, 1]

    result = get_metrics(
        f"Logistic Regression C={C}",
        y_valid,
        valid_prob
    )

    result["C"] = C

    lr_results.append(result)

lr_result_df = pd.DataFrame(lr_results)

lr_result_df = lr_result_df.sort_values(
    by="pr_auc",
    ascending=False
)

print("\nLogistic Regression tuning results")
print(lr_result_df)

lr_result_df.to_csv(
    "../data/lr_tuning_results.csv",
    index=False
)

# XGBoost tuning
print("\nStart XGBoost tuning")

xgb_results = []

pos_count = y_train.sum()
neg_count = len(y_train) - pos_count

scale_pos_weight = neg_count / pos_count

for params in XGB_PARAM_GRID:
    print("\nTraining XGBoost with params:")
    print(params)

    xgb_params = XGB_PARAMS.copy()
    xgb_params.update(params)
    xgb_params["scale_pos_weight"] = scale_pos_weight

    xgb_model = XGBClassifier(**xgb_params)

    xgb_model.fit(
        X_train,
        y_train,
        eval_set=[(X_valid, y_valid)],
        verbose=False
    )

    valid_prob = xgb_model.predict_proba(X_valid)[:, 1]

    result = get_metrics(
        (
            "XGBoost "
            f"n={params['n_estimators']}, "
            f"depth={params['max_depth']}, "
            f"lr={params['learning_rate']}"
        ),
        y_valid,
        valid_prob
    )

    result.update(params)

    xgb_results.append(result)

xgb_result_df = pd.DataFrame(xgb_results)

xgb_result_df = xgb_result_df.sort_values(
    by="pr_auc",
    ascending=False
)

print("\nXGBoost tuning results")
print(xgb_result_df)

xgb_result_df.to_csv(
    "../data/xgb_tuning_results.csv",
    index=False
)

# best parameters
print("\nBest Logistic Regression parameters")
print(lr_result_df.iloc[0])

print("\nBest XGBoost parameters")
print(xgb_result_df.iloc[0])

print("\nParameter tuning completed.")