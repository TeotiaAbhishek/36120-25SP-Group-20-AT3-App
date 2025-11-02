# app/main.py

from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import numpy as np
import datetime as dt

app = FastAPI(
    title="Crypto Price Prediction API",
    description="""
    This API provides next-day HIGH price predictions for a specific cryptocurrency using a trained ML model.
    
    **Endpoints:**
    - `/` : Overview
    - `/health/` : Health check
    - `/predict/<token>` : Predict next-day high price
    
    **Expected Output:**
    ```json
    {
        "token": "ETH",
        "date_predicted": "2025-11-02",
        "predicted_high": 3421.55
    }
    ```
    """,
    version="1.0.0"
)

# Load model and preprocessing artifacts
model = joblib.load("model/xgboost_model.pkl")
features_list = joblib.load("model/features_list.pkl")

# ======= Root Endpoint =======
@app.get("/")
def root():
    return {
        "project": "Crypto Investment Data Product - Ethereum API",
        "description": "Predicts next-day HIGH price for Ethereum (ETH).",
        "endpoints": {
            "/": "Project overview",
            "/health/": "Health check endpoint",
            "/predict/ETH": "Return next-day high price prediction for Ethereum"
        },
        "expected_input": "No user input required (prediction based on internal features).",
        "output_format": {
            "token": "ETH",
            "date_predicted": "YYYY-MM-DD",
            "predicted_high": "float"
        },
        "github_repo": "https://github.com/<your-username>/<your-fastapi-repo>"
    }


# ======= Health Check =======
@app.get("/health/")
def health_check():
    return {"status": 200, "message": "FastAPI server running successfully"}


# ======= Prediction Endpoint =======
@app.get("/predict/{token}")
def predict_price(token: str):

    if token.upper() != "ETH":
        raise HTTPException(status_code=400, detail="Only Ethereum (ETH) supported for now.")

    # === Dummy Features ===
    dummy_data = pd.DataFrame([{
        "open": 3400,
        "high": 3450,
        "low": 3380,
        "close": 3420,
        "SMA_7": 3410,
        "EMA_7": 3415,
        "volatility_7": 0.015,
        "momentum_ratio": 1.02,
        "price_range_ratio": 0.02,
        "RSI_14": 55,
        "returns": 0.004,
        "close_lag1": 3410,          
        "RSI_14_lag1": 53,            
        "SMA_7_lag1": 3405,        
        "EMA_7_lag1": 3410           
    }])


    # Reorder columns according to feature list
    dummy_data = dummy_data[features_list]

    # Make prediction
    pred = model.predict(dummy_data)[0]

    return {
        "token": token.upper(),
        "date_predicted": (dt.date.today() + dt.timedelta(days=1)).isoformat(),
        "predicted_high": float(round(pred, 2))
    }
