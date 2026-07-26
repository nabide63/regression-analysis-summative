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
- `POST /retrain` - upload a CSV of new labeled data to retrain the model

## Running it locally

```
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs to try it out.
