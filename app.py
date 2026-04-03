import requests
import streamlit as st
from collections import defaultdict
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="DEX Dashboard", layout="wide")

st.title("📊 Options DEX & GEX Dashboard")

api_key = st.text_input("Enter Polygon API Key", type="password")
symbol = st.text_input("Ticker Symbol", value="SPY")

if api_key and symbol:
    url = f"https://api.polygon.io/v3/snapshot/options/{symbol}?apiKey={api_key}"
    response = requests.get(url).json()

    total_dex = 0
    total_gex = 0
    dex_by_strike = defaultdict(float)
    gex_by_strike = defaultdict(float)

    for option in response.get("results", []):
        try:
            delta = option["greeks"]["delta"]
            gamma = option["greeks"]["gamma"]
            oi = option["open_interest"]
            strike = option["details"]["strike_price"]

            dex = delta * oi * 100
            gex = gamma * oi * 100

            total_dex += dex
            total_gex += gex

            dex_by_strike[strike] += dex
            gex_by_strike[strike] += gex
        except:
            continue

    col1, col2 = st.columns(2)
    col1.metric("Total DEX", round(total_dex, 2))
    col2.metric("Total GEX", round(total_gex, 2))

    st.markdown("## 📊 Market Overview")

    dex_df = pd.DataFrame({
        "Strike": list(dex_by_strike.keys()),
        "DEX": list(dex_by_strike.values())
    }).sort_values(by="Strike")

    gex_df = pd.DataFrame({
        "Strike": list(gex_by_strike.keys()),
        "GEX": list(gex_by_strike.values())
    }).sort_values(by="Strike")

    col1, col2 = st.columns(2)

    with col1:
        fig_dex = px.bar(dex_df, x="Strike", y="DEX", title="DEX by Strike")
        st.plotly_chart(fig_dex, use_container_width=True)

    with col2:
        fig_gex = px.bar(gex_df, x="Strike", y="GEX", title="GEX by Strike")
        st.plotly_chart(fig_gex, use_container_width=True)

    max_gex_strike = max(gex_by_strike, key=lambda x: abs(gex_by_strike[x]))
    st.subheader(f"📌 Key GEX Level: {max_gex_strike}")

    if total_gex < 0:
        st.error("⚠️ High volatility expected")
    else:
        st.success("✅ Market likely stable")

else:
    st.info("Enter API key and symbol to load data.")
