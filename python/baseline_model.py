#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseline models for user behavior purchase prediction
"""
# import libraries
import os
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

print("\nOriginal Training Label Distribution")
print(y_train.value_counts())
print(y_train.value_counts(normalize=True))

# baseline training sample information
train_pos_count = int(y_train.sum())
train_neg_count = int(len(y_train) - train_pos_count)
scale_pos_weight = train_neg_count / train_pos_count

print("Positive count:", train_pos_count)
print("Negative count:", train_neg_count)
print("scale_pos_weight:", scale_pos_weight)


# evaluation function
def evaluate_model(model_name, dataset_name, y_true, y_prob):

    y_pred = (y_prob >= 0.5).astype(int)

    result = {
        "model": model_name,
        "dataset": dataset_name,
        "sampling_method": "Baseline",
        "sampling_ratio": "Original",
        "train_positive_count": train_pos_count,
        "train_negative_count": train_neg_count,
        "scale_pos_weight": scale_pos_weight,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob),
        "pr_auc": average_precision_score(y_true, y_prob)
    }

    print(f"\n{model_name} - {dataset_name}")
    print("Accuracy:", result["accuracy"])
    print("Precision:", result["precision"])
    print("Recall:", result["recall"])
    print("F1:", result["f1"])
    print("ROC AUC:", result["roc_auc"])
    print("PR AUC:", result["pr_auc"])

    return result


all_results = []

# Logistic Regression baseline
print("\nTraining Logistic Regression...")

lr_model = LogisticRegression(**LR_PARAMS)

lr_model.fit(X_train, y_train)

valid_prob_lr = lr_model.predict_proba(X_valid)[:, 1]

result = evaluate_model(
    "Logistic Regression",
    "Validation",
    y_valid,
    valid_prob_lr
)
all_results.append(result)

test_prob_lr = lr_model.predict_proba(X_test)[:, 1]

result = evaluate_model(
    "Logistic Regression",
    "Test",
    y_test,
    test_prob_lr
)
all_results.append(result)

# XGBoost baseline
print("\nTraining XGBoost...")

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

result = evaluate_model(
    "XGBoost",
    "Validation",
    y_valid,
    valid_prob_xgb
)
all_results.append(result)

test_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

result = evaluate_model(
    "XGBoost",
    "Test",
    y_test,
    test_prob_xgb
)
all_results.append(result)


# save results
os.makedirs("../results", exist_ok=True)

results_df = pd.DataFrame(all_results)

results_df = results_df[
    [
        "model",
        "dataset",
        "sampling_method",
        "sampling_ratio",
        "train_positive_count",
        "train_negative_count",
        "scale_pos_weight",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "pr_auc"
    ]
]

validation_results = results_df[
    results_df["dataset"] == "Validation"
]

test_results = results_df[
    results_df["dataset"] == "Test"
]

results_df.to_csv(
    "../results/baseline_results.csv",
    index=False
)

validation_results.to_csv(
    "../results/baseline_validation.csv",
    index=False
)

test_results.to_csv(
    "../results/baseline_test.csv",
    index=False
)

print("\nBaseline Results Summary")
print(results_df)

print("\nResults saved:")
print("../results/baseline_results.csv")
print("../results/baseline_validation.csv")
print("../results/baseline_test.csv")

print("\nBaseline Model training completed.")