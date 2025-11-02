# Crypto Price Prediction API

This repository contains a **FastAPI service** that predicts the **next-day HIGH price** for a selected cryptocurrency (e.g., Ethereum) using a trained machine learning model.

This API is part of the **Crypto Investment Data Product** project (UTS 36120 - AT3), integrating with a Streamlit app and experimentation repository.

---

## Project Overview

- **Goal:** Predict the **next-day HIGH price** for a specific cryptocurrency based on historical OHLC (Open, High, Low, Close) and volume data.  
- **Crypto Covered:** Ethereum (ETH)  
- **Model Used:** e.g., XGBoostRegressor or chosen ML algorithm  
- **Deployment Target:** [Render.com](https://render.com)  
- **Frontend Integration:** [Streamlit App](https://streamlit.io)

---

## API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/` | GET | Overview of the project, endpoints, and expected inputs/outputs |
| `/health/` | GET | Health check endpoint |
| `/predict/<token>` | GET | Returns predicted next-day HIGH price for the selected token |

### Example Response
```json
{
  "token": "ETH",
  "date_predicted": "2025-11-02",
  "predicted_high": 3421.55
}
