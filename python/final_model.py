#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final model training using full data and best XGBoost parameters
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

def train_final_model(
        drop_features=None,
        threshold=0.5,
        save_prefix="final"
):
    
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
    
    # combine train and validation for final training
    train_valid_df = pd.concat(
        [train_df, valid_df],
        axis=0
    ).reset_index(drop=True)
    
    print("\nTrain + Valid shape:", train_valid_df.shape)
    print("Test shape:", test_df.shape)
    
    print("\nTrain + Valid label distribution")
    print(train_valid_df["label"].value_counts(normalize=True))
    
    print("\nTest label distribution")
    print(test_df["label"].value_counts(normalize=True))
    
    # features and labels
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
    
    print(X_train_valid.shape)
    
    X_test = test_df.drop(columns=drop_cols)
    y_test = test_df["label"]
    
    # feature selection
    if drop_features is not None:
        X_train_valid = X_train_valid.drop(
            columns=drop_features,
            errors="ignore"
        )
    
        X_test = X_test.drop(
            columns=drop_features,
            errors="ignore"
        )
    
        print("\nRemoved features:")
        print(drop_features)
    
        print(
            "\nNumber of features after selection:",
            X_train_valid.shape[1]
        )
    
    # evaluation function
    def evaluate_model(model_name, y_true, y_prob, threshold=0.5):
        y_pred = (y_prob >= threshold).astype(int)
    
        print(f"\n{model_name}")
    
        print("Accuracy:", accuracy_score(y_true, y_pred))
        print("Precision:", precision_score(y_true, y_pred, zero_division=0))
        print("Recall:", recall_score(y_true, y_pred, zero_division=0))
        print("F1:", f1_score(y_true, y_pred, zero_division=0))
        print("ROC AUC:", roc_auc_score(y_true, y_prob))
        print("PR AUC:", average_precision_score(y_true, y_prob))
    
        print("\nConfusion Matrix")
        print(confusion_matrix(y_true, y_pred))
    
        print("\nClassification Report")
        print(classification_report(y_true, y_pred, zero_division=0))
    
    # best XGBoost parameters from validation tuning
    best_xgb_params = XGB_PARAMS.copy()
    
    best_xgb_params.update({
        "n_estimators": 300,
        "max_depth": 5,
        "learning_rate": 0.05
    })
    
    pos_count = y_train_valid.sum()
    neg_count = len(y_train_valid) - pos_count
    
    best_xgb_params["scale_pos_weight"] = neg_count / pos_count
    
    # train final XGBoost model
    final_xgb_model = XGBClassifier(**best_xgb_params)
    
    print("\nTraining final XGBoost model...")
    
    final_xgb_model.fit(
        X_train_valid,
        y_train_valid,
        verbose=False
    )
    
    # final test evaluation
    test_prob = final_xgb_model.predict_proba(X_test)[:, 1]
    
    prediction_df = pd.DataFrame({
    "label": y_test,
    "prob": test_prob
    })

    prediction_df.to_csv(
        "../data/final_prediction.csv",
        index=False
    )
    
    evaluate_model(
        "Final XGBoost - Test",
        y_test,
        test_prob
    )
    
    # threshold tuning
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
        y_pred = (test_prob >= threshold).astype(int)
    
        result = {
            "threshold": threshold,
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0)
        }
    
        threshold_results.append(result)
    
    threshold_result_df = pd.DataFrame(threshold_results)
    
    print("\nThreshold tuning results")
    print(threshold_result_df)
    
    threshold_result_df.to_csv(
        "../data/threshold_tuning_results.csv",
        index=False
    )
    
    # feature importance
    feature_importance = pd.DataFrame({
        "feature": X_train_valid.columns,
        "importance": final_xgb_model.feature_importances_
    })
    
    feature_importance = feature_importance.sort_values(
        by="importance",
        ascending=False
    )
    
    print("\nTop 20 feature importance")
    print(feature_importance.head(20))
    
    # save results
    feature_importance.to_csv(
        "../data/final_xgb_feature_importance.csv",
        index=False
    )
    
    print("\nFinal model training completed.")

if __name__ == "__main__":
    train_final_model()
    
