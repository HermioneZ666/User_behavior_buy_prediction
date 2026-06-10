#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 16:27:07 2026

@author: hermionezhou
"""

# import libraries
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report
)

# Load data
df = pd.read_csv("../data/clean_feature_table.csv")

print("Data loaded successfully.")
print("Shape:", df.shape)

# Convert time and sort by time
df["sample_time"] = pd.to_datetime(df["sample_time"])

df = df.sort_values("sample_time").reset_index(drop=True)

# Train / valid / test split by time
# Ratio: 7 : 2 : 1
n = len(df)

train_end = int(n * 0.7)
valid_end = int(n * 0.9)

train_df = df.iloc[:train_end]
valid_df = df.iloc[train_end:valid_end]
test_df = df.iloc[valid_end:]

print("\nTrain shape:", train_df.shape)
print("Valid shape:", valid_df.shape)
print("Test shape:", test_df.shape)

print("\nTrain label distribution:")
print(train_df["label"].value_counts(normalize=True))

print("\nValid label distribution:")
print(valid_df["label"].value_counts(normalize=True))

print("\nTest label distribution:")
print(test_df["label"].value_counts(normalize=True))

# Prepare features and label
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

print("\nFeature number:", X_train.shape[1])

# Evaluation function
def evaluate_model(model_name, y_true, y_pred, y_prob):
    
    print(f"\n{model_name} Evaluation")
    
    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred, zero_division=0))
    print("Recall:", recall_score(y_true, y_pred, zero_division=0))
    print("F1:", f1_score(y_true, y_pred, zero_division=0))
    print("ROC AUC:", roc_auc_score(y_true, y_prob))
    print("PR AUC:", average_precision_score(y_true, y_prob))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, zero_division=0))

# %%
# Logistic Regression baseline
linear_model = LogisticRegression(
    max_iter=500,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)

print("\nTraining Logistic Regression...")

linear_model.fit(X_train, y_train)

valid_prob_linear = linear_model.predict_proba(X_valid)[:, 1]
test_prob_linear = linear_model.predict_proba(X_test)[:, 1]

evaluate_model(
    "Linear Model - Validation",
    y_valid,
    valid_prob_linear
)

evaluate_model(
    "Linear Model - Test",
    y_test,
    test_prob_linear
)

# %%
# XGBoost
pos_count = y_train.sum()
neg_count = len(y_train) - pos_count

scale_pos_weight = neg_count / pos_count

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="auc",
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    n_jobs=-1
)

print("\nTraining XGBoost...")

xgb_model.fit(
    X_train,
    y_train,
    eval_set=[(X_valid, y_valid)],
    verbose=True
)

valid_prob_xgb = xgb_model.predict_proba(X_valid)[:, 1]

evaluate_model(
    "XGBoost - Validation",
    y_valid,
    valid_prob_xgb
)

# Test evaluation using XGBoost
test_prob_xgb = xgb_model.predict_proba(X_test)[:, 1]

evaluate_model(
    "XGBoost - Test",
    y_test,
    test_prob_xgb
)

# Feature importance
feature_importance = pd.DataFrame({
    "feature": X_train.columns,
    "importance": xgb_model.feature_importances_
}).sort_values(
    by="importance",
    ascending=False
)

print("\nTop 20 XGBoost feature importance")
print(feature_importance.head(20))

print("\nModel training completed.")