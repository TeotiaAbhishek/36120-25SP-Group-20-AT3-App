import streamlit as st
import plotly.express as px
import pandas as pd
import requests

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Crypto Explorer", layout="wide")

# ------------------------------------------------------------
# INITIALISE SESSION STATE FOR PAGE NAVIGATION
# ------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Price Analysis"  # default page

# Function to switch pages internally
def go_to(page_name: str):
    st.session_state.page = page_name

# ------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------
page = st.sidebar.radio(
    "Navigate",
    ["Price Analysis", "T+1 Prediction"],
    index=0 if st.session_state.page == "Price Analysis" else 1,
    key="sidebar_radio",
)

# Keep sidebar and button navigation in sync
if page != st.session_state.page:
    st.session_state.page = page

# ------------------------------------------------------------
# PAGE 1: PRICE ANALYSIS
# ------------------------------------------------------------
if st.session_state.page == "Price Analysis":
    st.title("Cryptocurrency Explorer")
    st.subheader("Price Analysis")

    try:
        df = pd.read_csv("bitcoin_usd_proc.csv")
        df = df[df["date"] < "2025-10-13"]
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

    # --- Prediction Button ---
    st.markdown("---")
    st.markdown("###Want to see the predicted high for T+1?")
    if st.button("Get Prediction for T+1"):
        go_to("T+1 Prediction")
        st.experimental_rerun()  # re-render the app immediately

# ------------------------------------------------------------
# PAGE 2: T+1 PREDICTION
# ------------------------------------------------------------
elif st.session_state.page == "T+1 Prediction":
    st.title("Bitcoin T+1 High Price Prediction")
    st.subheader("Powered by Machine Learning Model (Stacking Regressor)")

    API_URL = "https://three6120-25sp-25224496-at3-api.onrender.com/predict_next_day"

    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            result = response.json()
            st.success("Prediction Fetched Successfully!")

            st.metric("Last Date in Data", result.get("last_date_in_data", "N/A"))
            st.metric("Predicted Date", result.get("predicted_date", "N/A"))
            st.metric("Predicted High (USD)", f"${result.get('predicted_high_tplus1', 'N/A'):,.2f}")
        else:
            st.error(f"API Error: {response.status_code}")

    except Exception as e:
        st.error("Could not connect to the API.")
        st.write(e)

    st.markdown("---")
    if st.button("Back to Price Analysis"):
        go_to("Price Analysis")
        st.experimental_rerun()
