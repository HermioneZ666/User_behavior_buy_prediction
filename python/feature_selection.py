#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature selection experiment for final XGBoost model
"""

# import libraries
import pandas as pd

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

from config import *

# load full data
df = pd.read_csv("../data/clean_feature_table.csv")

print("Full data loaded successfully.")
print("Shape:", df.shape)

# time split
df["sample_time"] = pd.to_datetime(df["sample_time"])

df = df.sort_values("sample_time").reset_index(drop=True)

n = len(df)

train_end = int(n * TRAIN_RATIO)
valid_end = int(n * (TRAIN_RATIO + VALID_RATIO))

train_df = df.iloc[:train_end]
valid_df = df.iloc[train_end:valid_end]
test_df = df.iloc[valid_end:]

# Combine train and validation for final training

train_valid_df = pd.concat(
    [train_df, valid_df],
    axis=0
).reset_index(drop=True)

print("\nTrain + Valid shape:", train_valid_df.shape)
print("Test shape:", test_df.shape)

# Prepare features and labels

drop_cols = [
    "sample_id",
    "user_id",
    "item_id",
    "item_category",
    "sample_time",
    "label"
]

X_train_valid = train_valid_df.drop(columns=drop_cols)
y_train_valid = train_valid_df["label"]

X_test = test_df.drop(columns=drop_cols)
y_test = test_df["label"]

# Manually selected redundant features to remove
drop_features = [
    "ui_has_fav_7d",
    "ui_has_cart_7d",
    "ui_has_buy_7d",

    "item_night_buy_cnt_7d",
    "item_weekend_buy_cnt_7d",

    "cate_night_buy_cnt_7d",
    "cate_weekend_buy_cnt_7d"
]

drop_features = [
    col
    for col in drop_features
    if col in X_train_valid.columns
]

print("\nRemoved features")
print(drop_features)

print("\nOriginal feature number:", X_train_valid.shape[1])

X_train_valid = X_train_valid.drop(columns=drop_features)

X_test = X_test.drop(columns=drop_features)

print("Selected feature number:", X_train_valid.shape[1])

# evaluation function
def evaluate_model(model_name, y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)

    result = {
        "model": model_name,
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, y_prob),
        "pr_auc": average_precision_score(y_true, y_prob)
    }

    print(f"\n{model_name}")

    print("Threshold:", threshold)
    print("Accuracy:", result["accuracy"])
    print("Precision:", result["precision"])
    print("Recall:", result["recall"])
    print("F1:", result["f1"])
    print("ROC AUC:", result["roc_auc"])
    print("PR AUC:", result["pr_auc"])

    print("\nConfusion Matrix")
    print(confusion_matrix(y_true, y_pred))

    print("\nClassification Report")
    print(classification_report(y_true, y_pred, zero_division=0))

    return result


# Best XGBoost parameters from previous tuning

best_xgb_params = XGB_PARAMS.copy()

best_xgb_params.update({
    "n_estimators": 300,
    "max_depth": 5,
    "learning_rate": 0.05
})

pos_count = y_train_valid.sum()
neg_count = len(y_train_valid) - pos_count

best_xgb_params["scale_pos_weight"] = neg_count / pos_count


# Train XGBoost model with selected features

model = XGBClassifier(**best_xgb_params)

print("\nTraining XGBoost with selected features...")

model.fit(
    X_train_valid,
    y_train_valid,
    verbose=False
)


# Test evaluation

test_prob = model.predict_proba(X_test)[:, 1]

result_05 = evaluate_model(
    "XGBoost with selected features - Test",
    y_test,
    test_prob,
    threshold=0.5
)


# threshold comparison
threshold_list = [
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9
]

threshold_results = []

for threshold in threshold_list:

    result = evaluate_model(
        "XGBoost with selected features - Threshold Test",
        y_test,
        test_prob,
        threshold=threshold
    )

    threshold_results.append(result)


threshold_result_df = pd.DataFrame(threshold_results)

print("\nThreshold results with selected features")
print(threshold_result_df)

# Feature importance after selection

feature_importance = pd.DataFrame({
    "feature": X_train_valid.columns,
    "importance": model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nTop 20 feature importance after selection")
print(feature_importance.head(20))


# Save results

threshold_result_df.to_csv(
    "../data/feature_selection_threshold_results.csv",
    index=False
)

feature_importance.to_csv(
    "../data/feature_selection_importance.csv",
    index=False
)

selected_feature_summary = pd.DataFrame({
    "removed_feature": drop_features
})

selected_feature_summary.to_csv(
    "../data/removed_features.csv",
    index=False
)

print("\nFeature selection experiment completed.")