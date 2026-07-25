"""
Builds and retrains the milk yield pipeline.

Mirrors exactly what task1_regression_analysis/multivariate.ipynb does for the
winning model (LinearRegression): StandardScaler on numeric features,
OneHotEncoder on categorical features, wrapped together with the model in one
sklearn Pipeline so preprocessing can never drift out of sync with the model
at prediction time.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from features import ALL_FEATURES, CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET

RANDOM_STATE = 42


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", LinearRegression()),
    ])


def validate_training_columns(df: pd.DataFrame) -> None:
    required = set(ALL_FEATURES + [TARGET])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Uploaded data is missing required columns: {sorted(missing)}")


def retrain_pipeline(combined_df: pd.DataFrame) -> tuple[Pipeline, dict]:
    """Fits a fresh pipeline on combined_df and returns it with test metrics."""
    X = combined_df[ALL_FEATURES]
    y = combined_df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)

    metrics = {
        "train_r2": round(float(r2_score(y_train, train_pred)), 4),
        "test_r2": round(float(r2_score(y_test, test_pred)), 4),
        "test_rmse": round(float(np.sqrt(mean_squared_error(y_test, test_pred))), 4),
    }
    return pipeline, metrics
