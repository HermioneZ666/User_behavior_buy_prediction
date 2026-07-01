#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Over sampling experiment on sampled data 
"""

# import libraires
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
# sort by sample_time and split data into train / validation / test
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
    sampling_ratio,
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
        "sampling_method": "RandomOverSampling",
        "sampling_ratio": sampling_ratio,
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

    print(f"\n{model_name} - {dataset_name} - Sampling ratio: {sampling_ratio}")
    print("Accuracy:", result["accuracy"])
    print("Precision:", result["precision"])
    print("Recall:", result["recall"])
    print("F1:", result["f1"])
    print("ROC AUC:", result["roc_auc"])
    print("PR AUC:", result["pr_auc"])

    return result


# random over sampling experiment: test different sampling_strategy values: sampling_strategy = positive / negative after resampling
sampling_list = [
    0.05,
    0.1,
    0.2,
    0.3,
    0.5,
    0.7,
    1.0
]

all_results = []

for sampling_ratio in sampling_list:

    print("\n" + "=" * 80)
    print(f"Random Over Sampling: sampling_strategy = {sampling_ratio}")
    print("=" * 80)

    # apply random over sampling only on training set
    # validation and test sets keep original distribution
    sampler = RandomOverSampler(
        sampling_strategy=sampling_ratio,
        random_state=42
    )

    X_train_over, y_train_over = sampler.fit_resample(
        X_train,
        y_train
    )

    train_pos_count = int(y_train_over.sum())
    train_neg_count = int(len(y_train_over) - train_pos_count)

    # keep the same logic as baseline model:
    # calculate scale_pos_weight based on current training data
    scale_pos_weight = train_neg_count / train_pos_count

    print("\nOver-sampled training label distribution:")
    print(y_train_over.value_counts())
    print(y_train_over.value_counts(normalize=True))
    print("Positive count:", train_pos_count)
    print("Negative count:", train_neg_count)
    print("scale_pos_weight:", scale_pos_weight)

    # Logistic Regression baseline: train Logistic Regression on over-sampled training data
    print("\nTraining Logistic Regression...")

    lr_model = LogisticRegression(**LR_PARAMS)

    lr_model.fit(
        X_train_over,
        y_train_over
    )

    valid_prob_lr = lr_model.predict_proba(X_valid)[:, 1]

    result = evaluate_model(
        model_name="Logistic Regression",
        dataset_name="Validation",
        sampling_ratio=sampling_ratio,
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
        sampling_ratio=sampling_ratio,
        train_pos_count=train_pos_count,
        train_neg_count=train_neg_count,
        scale_pos_weight=scale_pos_weight,
        y_true=y_test,
        y_prob=test_prob_lr
    )

    all_results.append(result)

    # XGBoost baseline: train XGBoost on over-sampled training data
    print("\nTraining XGBoost...")

    xgb_params = XGB_PARAMS.copy()

    xgb_params["scale_pos_weight"] = scale_pos_weight

    xgb_model = XGBClassifier(**xgb_params)

    xgb_model.fit(
        X_train_over,
        y_train_over,
        eval_set=[(X_valid, y_valid)],
        verbose=False
    )

    valid_prob_xgb = xgb_model.predict_proba(X_valid)[:, 1]

    result = evaluate_model(
        model_name="XGBoost",
        dataset_name="Validation",
        sampling_ratio=sampling_ratio,
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
        sampling_ratio=sampling_ratio,
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


# display and save validation results: use validation set to select the best sampling ratio
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


# display test results
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


# save full results
os.makedirs("../results", exist_ok=True)

validation_results.to_csv(
    "../results/random_over_sampling_validation.csv",
    index=False
)

test_results.to_csv(
    "../results/random_over_sampling_test.csv",
    index=False
)

results_df.to_csv(
    "../results/random_over_sampling_results.csv",
    index=False
)

print("\nResults saved:")
print("../results/random_over_sampling_results.csv")
print("../results/random_over_sampling_validation.csv")
print("../results/random_over_sampling_test.csv")
print("\nRandom Over Sampling experiment completed.")