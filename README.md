# Dairy Cattle Milk Yield Predictor — Regression Analysis Summative

## Mission & Problem Statement

 Mission is to use software engineering and data analysis to build practical tools that empower Busoga's livestock farmers to increase profitability and improve local nutrition. Problem: Small-scale dairy farmers there often make feeding and management decisions without knowing how those decisions affect milk production, which makes yields inconsistent and squeezes profitability.

## Dataset Description

The dataset contains **250,000 records and 37 columns** describing individual dairy cattle and their daily milk production. Each row represents one cow on one day, covering feeding, environmental, health/vaccination, and animal-profile characteristics alongside the target, `Milk_Yield_L`.

## Dataset Source

- **Name:** Cattle Health and Feeding Data
- **File used:** `global_cattle_milk_yield_prediction_dataset.csv`
- **Platform:** Kaggle
- **Link:** https://www.kaggle.com/datasets/shahhet2812/cattle-health-and-feeding-data
- **Owner:** shahhet2812

## Repository Structure

This repo is organised into the three tasks of the summative assignment:

```
regression-analysis-summative/
├── task1_regression_analysis/   # Data cleaning, EDA, model training & selection
│   ├── data/raw/                # Original Kaggle dataset (not committed, see below)
│   ├── data/processed/          # Cleaned/engineered data used for modelling
│   ├── models/                  # Saved best-model pipeline (.joblib)
│   ├── multivariate.ipynb       # The full analysis notebook
│   └── requirements.txt
├── task2_api/                   # FastAPI backend that serves the trained model
│   ├── main.py                  # App + /predict and /retrain endpoints
│   ├── features.py, schemas.py, train_utils.py
│   ├── models/                  # Same pipeline, copied in for the API to load
│   ├── data/training_data_sample.csv
│   ├── pyproject.toml, uv.lock  # uv-managed dependencies (source of truth)
│   └── requirements.txt         # auto-generated from uv.lock, for Render's build
└── task3_flutter_app/           # Flutter mobile app (Android/iOS/web) that consumes the API
    └── lib/
        ├── main.dart
        ├── models/feature_specs.dart
        ├── screens/predict_screen.dart
        └── services/api_service.dart
```

## Task 1 — Regression Analysis (`task1_regression_analysis/`)

The notebook (`multivariate.ipynb`) works through the full pipeline on the **Cattle Health and Feeding Data** dataset from Kaggle (250,000 rows, 37 columns, one row per cow per day):

1. **Data cleaning** — checked for missing values and duplicates (found none), fixed data types (`Date` to datetime, vaccine flags to `int8`).
2. **Feature engineering** — dropped identifier columns (`Cattle_ID`, `Farm_ID`, `Date`, `Region`, `Country`), one-hot encoded 6 categorical columns (Breed, Climate_Zone, Management_System, Lactation_Stage, Feed_Type, Season), and standardised the 25 numeric features with `StandardScaler` inside a `ColumnTransformer`.
3. **EDA** — a correlation heatmap and scatter plots showed `Previous_Week_Avg_Yield` is by far the strongest predictor (0.97 correlation with the target), while same-day feeding/environmental features correlate only weakly.
4. **Model training & comparison** — trained and compared four models on an 80/20 train/test split:

   | Model | Train R² | Test R² | Test RMSE | Test MAE |
   |---|---|---|---|---|
   | **Linear Regression** | 0.9430 | **0.9429** | **1.376 L** | **1.093 L** |
   | SGDRegressor (gradient descent) | 0.9427 | 0.9427 | 1.379 L | 1.096 L |
   | Random Forest | 0.9478 | 0.9419 | 1.388 L | 1.106 L |
   | Decision Tree | 0.9424 | 0.9389 | 1.424 L | 1.134 L |

   **Linear Regression** came out on top on the held-out test set and generalises well (train/test gap is negligible), so it's the model I carried forward.
5. **Saving** — the fitted preprocessing + Linear Regression steps are bundled into one `sklearn.Pipeline` and saved to `models/milk_yield_pipeline.joblib`, so a single `.predict()` call on raw cow data handles encoding, scaling and prediction together (with negative predictions clipped to 0, since milk yield can't go below zero).

To run the notebook yourself:

```
cd task1_regression_analysis
pip install -r requirements.txt
jupyter notebook multivariate.ipynb
```

## Task 2 — Prediction API (`task2_api/`)

A FastAPI backend that loads the pipeline saved in Task 1 and exposes it over HTTP.

### Live, publicly routable endpoint

The API is deployed on Render (not localhost) here:

**https://milk-yield-predictor-viec.onrender.com**

Interactive Swagger UI docs ( use to try `/predict` and `/retrain`):

**https://milk-yield-predictor-viec.onrender.com/docs**

> Note: this runs on Render's free tier, so it spins down after periods of inactivity. The first request after some idle time can take 30–60 seconds (occasionally returning a 503) while it wakes back up — just retry after a moment. Once it's warm, responses are instant.

### Endpoints

- `GET /` — basic status message
- `GET /health` — health check, also reports whether the model file loaded
- `POST /predict` — send one cow's feature values, get back a predicted daily milk yield in litres
- `POST /retrain` — upload a CSV of new labelled data to retrain the model immediately (manual, one-off)
- `POST /ingest` — upload a CSV of new labelled data to be queued for **automatic** retraining

### Automatic retraining on new data

A background loop (started in the app's lifespan) checks `data/incoming/` every 60 seconds. Any CSV queued there via `POST /ingest` is folded into the training set, the model is retrained and hot-swapped automatically, and the file is archived — so a model update is triggered by new data showing up, not by a person remembering to call `/retrain`.

### Running it locally

This project uses [uv](https://docs.astral.sh/uv/) for package and virtual environment management:

```
cd task2_api
uv sync
uv run uvicorn main:app --reload
```

`uv sync` reads `pyproject.toml` / `uv.lock` and creates a `.venv` with the exact pinned dependency versions, so there's nothing to activate by hand. Then open `http://127.0.0.1:8000/docs` to try it with Swagger UI locally.

> `requirements.txt` is still kept in `task2_api/` (regenerated from `uv.lock` via `uv export --no-hashes --no-dev -o requirements.txt`) purely so the Render deployment's pip-based build keeps working - it isn't meant to be edited by hand.

## Task 3 — Mobile App (`task3_flutter_app/`)

A Flutter app where you fill in a form with a cow's stats (age, weight, feeding, activity, environment, vaccines, etc.) and it calls the Task 2 API to get back a predicted daily milk yield.

### How to run the mobile app

1. **Install prerequisites**: [Flutter SDK](https://docs.flutter.dev/get-started/install) (this project targets Dart SDK `^3.12.1`) and either an Android emulator/device, iOS simulator/device, or a browser for the web build.
2. **Get into the app folder and fetch dependencies**:

   ```
   cd task3_flutter_app
   flutter pub get
   ```

3. **Run it**:

   ```
   flutter run
   ```

   Pick your target device/emulator when prompted (or pass `-d chrome` for the web build, `-d windows` for a Windows desktop build, etc.).

4. **Point it at the API**: the app is already configured to call the live Render API above by default, so it works out of the box with no setup. If you'd rather test against an API running on your own machine, tap the settings icon in the app bar and change the base URL:
   - Android emulator → `http://10.0.2.2:8000`
   - iOS simulator / desktop / web → `http://127.0.0.1:8000`

   (Remember to start the Task 2 API locally first if you do this — see the "Running it locally" instructions above.)

5. **Use the app**: fill in the cow's details on the prediction form and submit — the app sends them to `/predict` and displays the predicted daily milk yield.

> Note: since the live API is on Render's free tier, the very first prediction request after the API has been idle can take a little longer while it wakes up.

## Demo Video

A short (max 7-minute) walkthrough covering the mission, the API in Swagger UI, and the mobile app in action:

**[YouTube demo link — TODO: add before submission]**

## Tech Stack

- **Modelling**: Python, pandas, NumPy, scikit-learn, matplotlib, seaborn
- **API**: FastAPI, Pydantic, Uvicorn, joblib — deployed on Render
- **Mobile app**: Flutter/Dart
