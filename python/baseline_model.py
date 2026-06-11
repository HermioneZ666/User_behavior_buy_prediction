#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseline models for user behavior purchase prediction
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

# sample data for baseline model
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
def evaluate_model(model_name, y_true, y_prob):

    y_pred = (y_prob >= 0.5).astype(int)

    print("\n", model_name)

    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred, zero_division=0))
    print("Recall:", recall_score(y_true, y_pred, zero_division=0))
    print("F1:", f1_score(y_true, y_pred, zero_division=0))
    print("ROC AUC:", roc_auc_score(y_true, y_prob))
    print("PR AUC:", average_precision_score(y_true, y_prob))

# Logistic Regression baseline
print("\nTraining Logistic Regression...")

lr_model = LogisticRegression(**LR_PARAMS)

lr_model.fit(X_train, y_train)

valid_prob_lr = lr_model.predict_proba(X_valid)[:, 1]

evaluate_model(
    "Logistic Regression Validation",
    y_valid,
    valid_prob_lr
)

test_prob_lr = lr_model.predict_proba(X_test)[:, 1]

evaluate_model(
    "Logistic Regression Test",
    y_test,
    test_prob_lr
)

# XGBoost baseline
print("\nTraining XGBoost...")

pos_count = y_train.sum()
neg_count = len(y_train) - pos_count

scale_pos_weight = neg_count / pos_count

xgb_params = XGB_PARAMS.copy()

xgb_params["scale_pos_weight"] = scale_pos_weight

xgb_model = XGBClassifier(**xgb_params)

xgb_model.fit(
    X_train,
    y_train,
    eval_set=[(X_valid, y_valid)],
    verbose=False
)

valid_prob_xgb = xgb_model.predict_proba(X_valid)[:, 1]

evaluate_model(
    "XGBoost Validation",
    y_valid,
    valid_prob_xgb
)

test_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

evaluate_model(
    "XGBoost Test",
    y_test,
    test_prob_xgb
)

print("\nBaseline Model training completed.")