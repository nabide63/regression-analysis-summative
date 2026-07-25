"""
FastAPI service for the dairy cattle milk yield prediction model (Task 2).

Wraps the LinearRegression pipeline trained in
task1_regression_analysis/multivariate.ipynb behind two endpoints:
  - POST /predict  -> single-cow prediction
  - POST /retrain  -> retrain the model when new labeled data is uploaded

Run locally with: uvicorn main:app --reload
Interactive docs: http://127.0.0.1:8000/docs
"""

import io
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from features import ALL_FEATURES, TARGET
from schemas import CowFeatures, PredictionResponse, RetrainResponse
from train_utils import retrain_pipeline, validate_training_columns

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "milk_yield_pipeline.joblib"
TRAINING_DATA_PATH = BASE_DIR / "data" / "training_data_sample.csv"

app = FastAPI(
    title="Milk Yield Prediction API",
    description=(
        "Predicts a dairy cow's daily milk yield (litres) from feeding, "
        "environmental and animal-related characteristics. Backs the "
        "Task 3 Flutter app for the Busoga dairy farmer mission."
    ),
    version="1.0.0",
)

# --- CORS ---
# This API has no authentication and serves a single, non-sensitive read
# (a milk yield number) plus a retrain operation gated only by uploading a
# correctly-shaped CSV - there is no user data, cookies or session state to
# protect. So we allow any origin (allow_origins=["*"]) to reach it, since
# the Flutter app may be tested as a web build from an unpredictable local
# dev origin (e.g. http://localhost:<random port>) and Swagger UI's "Try it
# out" button, and graders opening the docs from their own machines, all
# need to call this API from origins we cannot list in advance.
# What IS restricted:
#   - allow_methods is limited to GET and POST, since the API only ever
#     reads (health check, docs) or accepts new data (predict, retrain) -
#     there is no PUT/PATCH/DELETE route, so those verbs are never allowed.
#   - allow_credentials is False, because we allow_origins=["*"]; the CORS
#     spec forbids combining a wildcard origin with credentialed requests,
#     and we don't use cookies/auth headers anyway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_model = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(status_code=503, detail="Model file not found on server.")
        _model = joblib.load(MODEL_PATH)
    return _model


@app.get("/")
def root():
    return {"message": "Milk Yield Prediction API is running. See /docs for the Swagger UI."}


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL_PATH.exists()}


@app.post("/predict", response_model=PredictionResponse)
def predict(cow: CowFeatures):
    model = get_model()
    input_df = pd.DataFrame([cow.model_dump()])
    raw_prediction = model.predict(input_df)[0]
    prediction = round(max(0.0, float(raw_prediction)), 2)
    return PredictionResponse(predicted_milk_yield_l=prediction)


@app.post("/retrain", response_model=RetrainResponse)
def retrain(file: UploadFile = File(..., description="CSV with the 31 feature columns plus Milk_Yield_L")):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    try:
        new_data = pd.read_csv(io.BytesIO(file.file.read()))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    try:
        validate_training_columns(new_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    existing_data = pd.read_csv(TRAINING_DATA_PATH)
    combined = pd.concat(
        [existing_data, new_data[ALL_FEATURES + [TARGET]]],
        ignore_index=True,
    )

    new_pipeline, metrics = retrain_pipeline(combined)

    joblib.dump(new_pipeline, MODEL_PATH)
    combined.to_csv(TRAINING_DATA_PATH, index=False)

    global _model
    _model = new_pipeline

    return RetrainResponse(
        message="Model retrained and saved successfully.",
        rows_added=len(new_data),
        total_training_rows=len(combined),
        train_r2=metrics["train_r2"],
        test_r2=metrics["test_r2"],
        test_rmse=metrics["test_rmse"],
    )
