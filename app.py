import streamlit as st
import plotly.express as px
import pandas as pd
import requests

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Crypto Explorer", layout="wide")

# ------------------------------------------------------------
# HELPER FUNCTIONS (with caching)
# ------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    """Load and preprocess Bitcoin CSV data once."""
    df = pd.read_csv("bitcoin_usd_proc.csv")
    df = df[df["date"] < "2025-10-13"]
    return df

@st.cache_data(ttl=600, show_spinner=False)
def fetch_prediction(api_url: str):
    """Fetch T+1 prediction from API (cached for 10 minutes)."""
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------
# INITIALISE SESSION STATE
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Price Analysis"

def go_to(page_name: str):
    st.session_state.page = page_name
    st.rerun()

# ------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------
page = st.sidebar.radio(
    "Navigate",
    ["Price Analysis", "T+1 Prediction"],
    index=0 if st.session_state.page == "Price Analysis" else 1,
)

if page != st.session_state.page:
    st.session_state.page = page

# ------------------------------------------------------------
# PAGE 1: PRICE ANALYSIS
# ------------------------------------------------------------
if st.session_state.page == "Price Analysis":
    st.title("Cryptocurrency Explorer")
    st.subheader("Price Analysis")

    with st.spinner("Loading price data..."):
        try:
            df = load_data()
        except FileNotFoundError:
            st.error("bitcoin_usd_proc.csv not found.")
            st.stop()

    if df.empty:
        st.warning("No OHLC data available for this coin.")
    else:
        fig = px.line(
            df, x="date", y="price_close",
            title="Bitcoin USD Close Price Over Time",
            template="plotly_dark",
        )
        fig.update_traces(line=dict(width=2, color="#00bcd4"))
        fig.update_layout(
            title_font_size=18,
            margin=dict(l=10, r=10, t=50, b=10),
            height=500,
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("Want to see the predicted high for T+1?")
    if st.button("Get Prediction for T+1"):
        go_to("T+1 Prediction")

# ------------------------------------------------------------
# PAGE 2: T+1 PREDICTION
# ------------------------------------------------------------
elif st.session_state.page == "T+1 Prediction":
    st.title("Bitcoin T+1 High Price Prediction")
    st.subheader("Powered by Machine Learning Model (Stacking Regressor)")

    API_URL = "https://three6120-25sp-25224496-at3-api.onrender.com/predict_next_day"

    with st.spinner("Fetching prediction..."):
        result = fetch_prediction(API_URL)

    if "error" in result:
        st.error(f"Could not fetch prediction: {result['error']}")
    else:
        st.success("Prediction Fetched Successfully!")
        st.metric("Last Date in Data", result.get("last_date_in_data", "N/A"))
        st.metric("Predicted Date", result.get("predicted_date", "N/A"))
        st.metric("Predicted High (USD)", f"${result.get('predicted_high_tplus1', 'N/A'):,.2f}")

    st.markdown("---")
    if st.button("Back to Price Analysis"):
        go_to("Price Analysis")
