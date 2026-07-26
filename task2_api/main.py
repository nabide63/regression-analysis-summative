"""
FastAPI service for my dairy cattle milk yield prediction model (Task 2).

This basically wraps the LinearRegression pipeline I trained in
task1_regression_analysis/multivariate.ipynb and exposes it as a few endpoints:
  - POST /predict  -> get a prediction for one cow
  - POST /retrain  -> retrain the model immediately when I upload new labeled data
  - POST /ingest   -> queue new labeled data for the background loop to retrain on automatically

Run it locally with: uvicorn main:app --reload
Then check the interactive docs at: http://127.0.0.1:8000/docs
"""

import asyncio
import io
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from features import ALL_FEATURES, TARGET
from schemas import CowFeatures, IngestResponse, PredictionResponse, RetrainResponse
from train_utils import process_incoming_dir, retrain_pipeline, validate_training_columns

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "milk_yield_pipeline.joblib"
TRAINING_DATA_PATH = BASE_DIR / "data" / "training_data_sample.csv"
INCOMING_DIR = BASE_DIR / "data" / "incoming"

# How often the background loop checks data/incoming/ for new labeled data
# and, if it finds any, automatically retrains and swaps the model in place.
AUTO_RETRAIN_INTERVAL_SECONDS = 60


async def _auto_retrain_loop() -> None:
    while True:
        await asyncio.sleep(AUTO_RETRAIN_INTERVAL_SECONDS)
        try:
            metrics = await asyncio.to_thread(
                process_incoming_dir, INCOMING_DIR, TRAINING_DATA_PATH, MODEL_PATH
            )
        except Exception as exc:  # noqa: BLE001 - a bad file shouldn't kill the loop
            print(f"[auto-retrain] failed: {exc}")
            continue
        if metrics is not None:
            global _model
            _model = joblib.load(MODEL_PATH)
            print(f"[auto-retrain] picked up new data and retrained: {metrics}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    task = asyncio.create_task(_auto_retrain_loop())
    yield
    task.cancel()


app = FastAPI(
    title="Milk Yield Prediction API",
    description=(
        "Predicts a dairy cow's daily milk yield (litres) from feeding, "
        "environmental and animal-related characteristics. Backs the "
        "Task 3 Flutter app for the Busoga dairy farmer mission."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS ---
# I don't actually need a wildcard origin here. My two real clients are:
#   - the Task 3 Flutter app's native Android/iOS builds, which never send an
#     Origin header at all - CORS is a browser-only mechanism, so it simply
#     doesn't apply to them.
#   - Swagger UI's "Try it out" button on /docs, which is served from this
#     same Render domain - that makes it a same-origin request, which is also
#     never subject to CORS.
# The only genuinely cross-origin case is a Flutter *web* build hitting this
# API from a local dev server during `flutter run -d chrome` (a random
# localhost/127.0.0.1 port each run), so instead of allow_origins=["*"] I
# match that with a regex rather than opening the door to every origin.
# What's locked down beyond that:
#   - allow_methods only allows GET and POST, since this API only ever reads
#     (health check, docs) or takes in new data (predict, retrain/ingest) -
#     I never use PUT/PATCH/DELETE so those are left out.
#   - allow_headers is just Content-Type, the only header my clients send.
#   - allow_credentials is False since I'm not using cookies or auth headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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


@app.post("/ingest", response_model=IngestResponse)
def ingest(file: UploadFile = File(..., description="CSV with the 31 feature columns plus Milk_Yield_L")):
    """Queues new labeled data for automatic retraining.

    Unlike /retrain (which retrains immediately, for a manual one-off), this
    just drops the file in data/incoming/. The background loop started in
    the app's lifespan picks it up on its own within
    AUTO_RETRAIN_INTERVAL_SECONDS and retrains without anyone calling an
    endpoint to say "retrain now" - the model update is triggered by the
    new data itself, not by a person.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    raw_bytes = file.file.read()
    try:
        incoming_df = pd.read_csv(io.BytesIO(raw_bytes))
        validate_training_columns(incoming_df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    dest = INCOMING_DIR / f"{uuid4().hex}_{file.filename}"
    dest.write_bytes(raw_bytes)

    return IngestResponse(
        message=(
            f"{len(incoming_df)} row(s) queued. The model auto-retrains on "
            f"new data within {AUTO_RETRAIN_INTERVAL_SECONDS} seconds."
        ),
        rows_queued=len(incoming_df),
    )
