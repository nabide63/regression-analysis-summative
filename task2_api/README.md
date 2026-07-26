# Milk Yield Prediction API

FastAPI backend for Task 2 of my regression analysis summative. It wraps the
LinearRegression pipeline I trained in
`task1_regression_analysis/multivariate.ipynb` and serves it as an API, so my
Task 3 Flutter app can send in a cow's stats and get back a predicted daily
milk yield.

## Live API

Deployed on Render here:

https://milk-yield-predictor-viec.onrender.com

Interactive docs (Swagger UI): https://milk-yield-predictor-viec.onrender.com/docs

Note: this is Render's free tier, so it spins down when idle. The first
request after a while can take 30-60 seconds (sometimes even return a 503)
while it wakes back up - just retry after a moment. Once it's warm it
responds instantly.

## Endpoints

- `GET /` - basic status message
- `GET /health` - health check, also tells you if the model file loaded
- `POST /predict` - send a single cow's features, get back a predicted milk yield
- `POST /retrain` - upload a CSV of new labeled data to retrain the model immediately (manual, one-off)
- `POST /ingest` - upload a CSV of new labeled data to be picked up automatically by the background retraining loop (see below), instead of retraining immediately

### Automatic retraining on new data

Besides the manual `/retrain` endpoint, there's a background loop (started in the app's `lifespan`) that checks `data/incoming/` every 60 seconds. Any CSV dropped there via `POST /ingest` gets folded into the training set, the model is retrained and swapped in automatically, and the file is archived to `data/incoming/processed/` - no one has to remember to trigger a retrain by hand once new data shows up.

## Running it locally

This project uses [uv](https://docs.astral.sh/uv/) for package and virtual environment
management. Install uv first (see their install docs), then from this folder:

```
uv sync
uv run uvicorn main:app --reload
```

`uv sync` reads `pyproject.toml` / `uv.lock` and creates a `.venv` with the exact
pinned versions - no need to create or activate a venv yourself. Then open
http://127.0.0.1:8000/docs to try it out.

`requirements.txt` is still kept in the repo (regenerated from `uv.lock` via
`uv export --no-hashes --no-dev -o requirements.txt`) purely so Render's
pip-based build stays working - it's not meant to be edited by hand.
