# milk_yield_predictor

Flutter app for Task 3 of my regression analysis summative. It's a simple form where you
enter a cow's stats (age, weight, feeding, activity, environment, vaccines, etc.) and it
sends them to my Task 2 FastAPI backend to get back a predicted daily milk yield.

## Live API

The backend is deployed on Render here:

https://milk-yield-predictor-viec.onrender.com

The app points to this URL by default, so you can just run it and start predicting. If you
want to test against a local backend instead, tap the settings icon in the app bar and change
the base URL (use `http://10.0.2.2:8000` if you're on an Android emulator hitting your own machine).

Note : Render free tier spins down when idle, so the first request after a while can take a
few seconds while it wakes back up.

## Running it

```
flutter pub get
flutter run 
```
