"""
Builds and retrains my milk yield pipeline.

This mirrors exactly what I did in task1_regression_analysis/multivariate.ipynb
for the winning model (LinearRegression): StandardScaler on the numeric
features, OneHotEncoder on the categorical features, all wrapped together with
the model in one sklearn Pipeline so preprocessing never drifts out of sync
with the model at prediction time.
"""

from pathlib import Path

import joblib
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
    """Trains a fresh pipeline on combined_df and hands back the test metrics too."""
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


def process_incoming_dir(incoming_dir: Path, training_data_path: Path, model_path: Path) -> dict | None:
    """Folds any CSVs waiting in incoming_dir into the training set and retrains.

    This is what makes retraining reactive instead of purely manual: /ingest
    just drops a file here, and the background loop in main.py calls this on
    a timer so a model update happens automatically once new data shows up -
    no one has to remember to call /retrain.
    Returns the new metrics (plus rows_added/total_training_rows), or None if
    there was nothing new to process.
    """
    csv_files = sorted(incoming_dir.glob("*.csv"))
    if not csv_files:
        return None

    new_frames = [pd.read_csv(f) for f in csv_files]
    for df in new_frames:
        validate_training_columns(df)

    existing_data = pd.read_csv(training_data_path)
    rows_added = sum(len(df) for df in new_frames)
    combined = pd.concat(
        [existing_data] + [df[ALL_FEATURES + [TARGET]] for df in new_frames],
        ignore_index=True,
    )

    pipeline, metrics = retrain_pipeline(combined)
    joblib.dump(pipeline, model_path)
    combined.to_csv(training_data_path, index=False)

    archive_dir = incoming_dir / "processed"
    archive_dir.mkdir(exist_ok=True)
    for f in csv_files:
        f.rename(archive_dir / f.name)

    metrics["rows_added"] = rows_added
    metrics["total_training_rows"] = len(combined)
    return metrics
