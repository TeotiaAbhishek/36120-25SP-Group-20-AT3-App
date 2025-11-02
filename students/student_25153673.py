import streamlit as st
import pandas as pd
import requests
import datetime as dt
import plotly.express as px

# -------------------------------
# CONFIG
# -------------------------------
CRYPTO_NAME = "Ethereum"
CRYPTO_SYMBOL = "ETH-USD"
COINDESK_API_URL = "https://data-api.coindesk.com/index/cc/v1/historical/days"
FASTAPI_URL = "https://fastapi-crypto.onrender.com/predict/ETH"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"

# -------------------------------
# FUNCTIONS
# -------------------------------
@st.cache_data(ttl=3600)
def get_historical_data(days=30):
    """Fetch historical OHLC data from CoinDesk."""
    try:
        params = {
            "market": "cadli",
            "instrument": CRYPTO_SYMBOL,
            "limit": days,
            "aggregate": 1,
            "fill": "true",
            "apply_mapping": "true",
            "response_format": "json"
        }
        r = requests.get(COINDESK_API_URL, params=params)
        r.raise_for_status()
        data = r.json()

        if "Data" not in data or not data["Data"]:
            st.warning("No historical data found.")
            return pd.DataFrame()

        df = pd.DataFrame(data["Data"])
        if "TIMESTAMP" in df.columns:
            df["date"] = pd.to_datetime(df["TIMESTAMP"], unit="s").dt.date
        elif "TIME" in df.columns:
            df["date"] = pd.to_datetime(df["TIME"], unit="s").dt.date
        else:
            raise KeyError("TIMESTAMP not found in CoinDesk response")

        df = df[["date", "OPEN", "HIGH", "LOW", "CLOSE"]]
        df.rename(columns=str.lower, inplace=True)
        return df.sort_values("date")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_social_trend():
    """Fetch crypto market sentiment (Fear & Greed Index)."""
    try:
        r = requests.get(FEAR_GREED_API_URL, params={"limit": 10, "format": "json"})
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data["data"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
        df["value"] = df["value"].astype(int)
        return df
    except Exception as e:
        st.error(f"Error fetching social trend: {e}")
        return pd.DataFrame()


def get_prediction():
    """Call the deployed FastAPI model."""
    try:
        response = requests.get(FASTAPI_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# STREAMLIT DASHBOARD
# -------------------------------
def render_student_tab():
    st.header(f"{CRYPTO_NAME} (ETH) Dashboard")

    # --- Section 1: Historical Prices ---
    st.subheader("Historical Price (Last 30 Days)")
    df = get_historical_data(days=30)

    if df.empty:
        st.warning("No data available from CoinDesk.")
        return

    fig = px.line(df, x="date", y="close", title=f"{CRYPTO_NAME} - 30 Day Closing Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    # --- Section 2: Statistics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Close (USD)", f"${df['close'].iloc[-1]:.2f}")
    col2.metric("Average 30-Day Close", f"${df['close'].mean():.2f}")
    col3.metric("30-Day Change (%)", f"{((df['close'].iloc[-1] / df['close'].iloc[0]) - 1)*100:.2f}%")

    st.divider()

    # --- Section 3: Social Trend ---
    st.subheader("Social Trend (Market Sentiment Index)")
    sentiment_df = get_social_trend()

    if not sentiment_df.empty:
        latest = sentiment_df.iloc[0]
        col1, col2 = st.columns(2)
        col1.metric("Current Sentiment", latest["value_classification"])
        col2.metric("Fear & Greed Score", latest["value"])

        trend_fig = px.line(
            sentiment_df,
            x="timestamp",
            y="value",
            title="Fear & Greed Index (Last 10 Days)",
            markers=True,
            color_discrete_sequence=["#f39c12"]
        )
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.warning("Could not load sentiment data.")

    st.divider()

    # --- Section 4: Model Prediction ---
    st.subheader("Next-Day High Price Prediction")
    pred = get_prediction()

    if "error" in pred:
        st.error(f"Failed to fetch prediction: {pred['error']}")
    else:
        st.success(f"Predicted HIGH for {pred['date_predicted']}: **${pred['predicted_high']:.2f}**")

    st.caption(f"Data source: CoinDesk & Alternative.me | Model served via FastAPI: {FASTAPI_URL}")


# -------------------------------
# RUN STREAMLIT APP
# -------------------------------
if __name__ == "__main__":
    render_student_tab()
