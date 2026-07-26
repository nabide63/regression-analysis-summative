"""
FastAPI service for my dairy cattle milk yield prediction model (Task 2).

This basically wraps the LinearRegression pipeline I trained in
task1_regression_analysis/multivariate.ipynb and exposes it as two endpoints:
  - POST /predict  -> get a prediction for one cow
  - POST /retrain  -> retrain the model when I upload new labeled data

Run it locally with: uvicorn main:app --reload
Then check the interactive docs at: http://127.0.0.1:8000/docs
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
# I'm not using any authentication here since this API only returns a milk
# yield number and lets you retrain by uploading a CSV - nothing sensitive,
# no user data, no cookies/sessions to worry about. That's why I open it up
# to any origin (allow_origins=["*"]): my Flutter app might run as a web
# build on some random localhost port, and Swagger UI's "Try it out" button
# plus my graders opening the docs from their own machines all need to hit
# this API from origins I can't list ahead of time.
# What I did lock down:
#   - allow_methods only allows GET and POST, since this API only ever reads
#     (health check, docs) or takes in new data (predict, retrain) - I never
#     use PUT/PATCH/DELETE so those are left out.
#   - allow_credentials is False because you can't mix a wildcard origin with
#     credentialed requests (the CORS spec doesn't allow that combo), and I'm
#     not using cookies or auth headers anyway.
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
