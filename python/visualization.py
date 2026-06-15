#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization for final model results
"""

# import libraries
import pandas as pd
from sklearn.metrics import (
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)
import matplotlib.pyplot as plt

# load saved results

feature_importance = pd.read_csv(
    "../data/final_xgb_feature_importance.csv"
)

threshold_result_df = pd.read_csv(
    "../data/threshold_tuning_results.csv"
)


# Top 20 feature importance
top20 = feature_importance.head(20)

plt.figure(figsize=(8, 8))

plt.barh(
    top20["feature"],
    top20["importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Top 20 Feature Importance")

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "../figures/top20_feature_importance.png",
    dpi=300
)

plt.show()


# threshold tuning
plt.figure(figsize=(7, 5))

plt.plot(
    threshold_result_df["threshold"],
    threshold_result_df["f1"],
    marker="o"
)

plt.xlabel("Threshold")
plt.ylabel("F1 Score")
plt.title("Threshold Tuning")

plt.grid()

plt.tight_layout()

plt.savefig(
    "../figures/threshold_tuning.png",
    dpi=300
)

plt.show()

# precision and recall tradeoff
plt.figure(figsize=(7, 5))

plt.plot(
    threshold_result_df["threshold"],
    threshold_result_df["precision"],
    marker="o",
    label="Precision"
)

plt.plot(
    threshold_result_df["threshold"],
    threshold_result_df["recall"],
    marker="o",
    label="Recall"
)

plt.xlabel("Threshold")
plt.ylabel("Metric Value")
plt.title("Precision-Recall Tradeoff")

plt.grid()
plt.legend()

plt.tight_layout()

plt.savefig(
    "../figures/precision_recall_tradeoff.png",
    dpi=300
)

plt.show()

# %%
# read predicted probability data
prediction_df = pd.read_csv(
    "../data/final_prediction.csv"
)

y_test = prediction_df["label"]
test_prob = prediction_df["prob"]

# ROC Curve
fpr, tpr, _ = roc_curve(
    y_test,
    test_prob
)

roc_auc = roc_auc_score(
    y_test,
    test_prob
)

plt.figure(figsize=(6, 6))

plt.plot(
    fpr,
    tpr,
    label=f"ROC AUC = {roc_auc:.3f}"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()

plt.tight_layout()

plt.savefig(
    "../figures/roc_curve.png",
    dpi=300
)

plt.show()

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(
    y_test,
    test_prob
)

pr_auc = average_precision_score(
    y_test,
    test_prob
)

plt.figure(figsize=(6, 6))

plt.plot(
    recall,
    precision,
    label=f"PR AUC = {pr_auc:.3f}"
)

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend()

plt.tight_layout()

plt.savefig(
    "../figures/pr_curve.png",
    dpi=300
)

plt.show()

print("ROC Curve and PR Curve saved successfully.")


print("\nFigures saved successfully.")
