#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hermionezhou
"""

# sample
SAMPLE_SIZE = 1000000

TRAIN_RATIO = 0.7
VALID_RATIO = 0.2
TEST_RATIO = 0.1

# Logistic Regression baseline
LR_PARAMS = {
    "max_iter": 200,
    "class_weight": "balanced",
    "solver": "saga",
    "n_jobs": -1,
    "random_state": 42,
    "verbose": 1
}

# XGBoost baseline
XGB_PARAMS = {
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "random_state": 42,
    "n_jobs": -1
}

# Logistic Regression tuning
LR_C_LIST = [
    0.01,
    0.1,
    1,
    10
]

# XGBoost tuning
XGB_PARAM_GRID = [
    {
        "n_estimators": 100,
        "max_depth": 3,
        "learning_rate": 0.1
    },

    {
        "n_estimators": 100,
        "max_depth": 5,
        "learning_rate": 0.1
    },

    {
        "n_estimators": 100,
        "max_depth": 7,
        "learning_rate": 0.1
    },

    {
        "n_estimators": 300,
        "max_depth": 5,
        "learning_rate": 0.05
    },

    {
        "n_estimators": 300,
        "max_depth": 7,
        "learning_rate": 0.05
    }
]