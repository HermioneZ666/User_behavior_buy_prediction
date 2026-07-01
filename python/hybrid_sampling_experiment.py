#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid sampling experiment on sampled data
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
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

from config import *


# load data
df = pd.read_csv("../data/clean_feature_table.csv")
print("Original shape:", df.shape)


# sample data: keep the same sample size as baseline model
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

print("Train shape:", train_df.shape)
print("Valid shape:", valid_df.shape)
print("Test shape:", test_df.shape)


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


# evaluation function
def evaluate_model(
    model_name,
    dataset_name,
    over_ratio,
    under_ratio,
    train_pos_count,
    train_neg_count,
    scale_pos_weight,
    y_true,
    y_prob
):
    y_pred = (y_prob >= 0.5).astype(int)

    result = {
        "model": model_name,
        "dataset": dataset_name,
        "sampling_method": "HybridSampling",
        "over_sampling_ratio": over_ratio,
        "under_sampling_ratio": under_ratio,
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

    print(
        f"\n{model_name} - {dataset_name} - "
        f"Over ratio: {over_ratio}, Under ratio: {under_ratio}"
    )
    print("Accuracy:", result["accuracy"])
    print("Precision:", result["precision"])
    print("Recall:", result["recall"])
    print("F1:", result["f1"])
    print("ROC AUC:", result["roc_auc"])
    print("PR AUC:", result["pr_auc"])

    return result


# hybrid sampling experiment
# step 1: random Over Sampling increases positive samples
# step 2: random Under Sampling reduces negative samples
hybrid_strategy_list = [
    {"over_ratio": 0.05, "under_ratio": 0.1},
    {"over_ratio": 0.1, "under_ratio": 0.2},
    {"over_ratio": 0.2, "under_ratio": 0.3},
    {"over_ratio": 0.3, "under_ratio": 0.5},
    {"over_ratio": 0.5, "under_ratio": 0.7},
    {"over_ratio": 0.7, "under_ratio": 1.0}
]

all_results = []

for strategy in hybrid_strategy_list:

    over_ratio = strategy["over_ratio"]
    under_ratio = strategy["under_ratio"]

    print("\n" + "=" * 80)
    print(
        f"Hybrid Sampling: "
        f"over_sampling_strategy = {over_ratio}, "
        f"under_sampling_strategy = {under_ratio}"
    )
    print("=" * 80)

    # step 1: apply Random Over Sampling only on training set
    over_sampler = RandomOverSampler(
        sampling_strategy=over_ratio,
        random_state=42
    )

    X_train_over, y_train_over = over_sampler.fit_resample(
        X_train,
        y_train
    )

    print("\nAfter Random Over Sampling")
    print(y_train_over.value_counts())
    print(y_train_over.value_counts(normalize=True))

    # step 2: apply Random Under Sampling after over sampling
    under_sampler = RandomUnderSampler(
        sampling_strategy=under_ratio,
        random_state=42
    )

    X_train_hybrid, y_train_hybrid = under_sampler.fit_resample(
        X_train_over,
        y_train_over
    )

    train_pos_count = int(y_train_hybrid.sum())
    train_neg_count = int(len(y_train_hybrid) - train_pos_count)

    # keep the same logic as baseline model:
    # calculate scale_pos_weight based on current training data
    scale_pos_weight = train_neg_count / train_pos_count

    print("\nAfter Hybrid Sampling")
    print(y_train_hybrid.value_counts())
    print(y_train_hybrid.value_counts(normalize=True))
    print("Positive count:", train_pos_count)
    print("Negative count:", train_neg_count)
    print("scale_pos_weight:", scale_pos_weight)

    # Logistic Regression baseline
    print("\nTraining Logistic Regression...")

    lr_model = LogisticRegression(**LR_PARAMS)

    lr_model.fit(
        X_train_hybrid,
        y_train_hybrid
    )

    valid_prob_lr = lr_model.predict_proba(X_valid)[:, 1]

    result = evaluate_model(
        model_name="Logistic Regression",
        dataset_name="Validation",
        over_ratio=over_ratio,
        under_ratio=under_ratio,
        train_pos_count=train_pos_count,
        train_neg_count=train_neg_count,
        scale_pos_weight=scale_pos_weight,
        y_true=y_valid,
        y_prob=valid_prob_lr
    )

    all_results.append(result)

    test_prob_lr = lr_model.predict_proba(X_test)[:, 1]

    result = evaluate_model(
        model_name="Logistic Regression",
        dataset_name="Test",
        over_ratio=over_ratio,
        under_ratio=under_ratio,
        train_pos_count=train_pos_count,
        train_neg_count=train_neg_count,
        scale_pos_weight=scale_pos_weight,
        y_true=y_test,
        y_prob=test_prob_lr
    )

    all_results.append(result)

    # XGBoost baseline
    print("\nTraining XGBoost...")

    xgb_params = XGB_PARAMS.copy()

    xgb_params["scale_pos_weight"] = scale_pos_weight

    xgb_model = XGBClassifier(**xgb_params)

    xgb_model.fit(
        X_train_hybrid,
        y_train_hybrid,
        eval_set=[(X_valid, y_valid)],
        verbose=False
    )

    valid_prob_xgb = xgb_model.predict_proba(X_valid)[:, 1]

    result = evaluate_model(
        model_name="XGBoost",
        dataset_name="Validation",
        over_ratio=over_ratio,
        under_ratio=under_ratio,
        train_pos_count=train_pos_count,
        train_neg_count=train_neg_count,
        scale_pos_weight=scale_pos_weight,
        y_true=y_valid,
        y_prob=valid_prob_xgb
    )

    all_results.append(result)

    test_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

    result = evaluate_model(
        model_name="XGBoost",
        dataset_name="Test",
        over_ratio=over_ratio,
        under_ratio=under_ratio,
        train_pos_count=train_pos_count,
        train_neg_count=train_neg_count,
        scale_pos_weight=scale_pos_weight,
        y_true=y_test,
        y_prob=test_prob_xgb
    )

    all_results.append(result)


# save results
results_df = pd.DataFrame(all_results)

results_df = results_df[
    [
        "model",
        "dataset",
        "sampling_method",
        "over_sampling_ratio",
        "under_sampling_ratio",
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


# validation results
validation_results = results_df[
    results_df["dataset"] == "Validation"
].sort_values(
    by="pr_auc",
    ascending=False
)

print("\n" + "=" * 80)
print("Validation Results (Sorted by PR AUC)")
print("=" * 80)
print(validation_results)


# test results
test_results = results_df[
    results_df["dataset"] == "Test"
].sort_values(
    by="pr_auc",
    ascending=False
)

print("\n" + "=" * 80)
print("Test Results (Sorted by PR AUC)")
print("=" * 80)
print(test_results)


# full results
os.makedirs("../results", exist_ok=True)

validation_results.to_csv(
    "../results/hybrid_sampling_validation.csv",
    index=False
)

test_results.to_csv(
    "../results/hybrid_sampling_test.csv",
    index=False
)

results_df.to_csv(
    "../results/hybrid_sampling_results.csv",
    index=False
)

print("\nResults saved:")
print("../results/hybrid_sampling_results.csv")
print("../results/hybrid_sampling_validation.csv")
print("../results/hybrid_sampling_test.csv")
print("\nHybrid Sampling experiment completed.")