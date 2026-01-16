import streamlit as st
import pandas as pd
from engine.forecast_engine import build_monthly_timeseries, forecast_2026, build_kit_plan

st.set_page_config(page_title="UIDAI Forecast Engine", layout="wide")

st.title("🔮 UIDAI Forecast Engine — 2026 Biometric Demand Planning")

DATA_PATH = "output/clean_monthly_load.csv"

# Load dataset
try:
    df = pd.read_csv(DATA_PATH)
except:
    st.error("❌ Clean dataset not found. Please upload and validate data first.")
    st.stop()

# Preview
st.subheader("📄 Clean Dataset Preview")
st.dataframe(df.head(15), use_container_width=True)

# Forecast button
st.subheader("🚀 Forecast Controls")

if st.button("Run 2026 Forecast Engine"):

    with st.spinner("Running AI Forecast Engine..."):

        monthly = build_monthly_timeseries(df)
        forecast = forecast_2026(monthly)
        plan = build_kit_plan(forecast)

        plan.to_csv("output/forecast_2026.csv", index=False)

    st.success("✅ Forecast Generated Successfully")
    st.subheader("📊 2026 Biometric Load Forecast")
    st.dataframe(plan, use_container_width=True)

    st.download_button(
        "⬇ Download Forecast Report",
        data=plan.to_csv(index=False),
        file_name="UIDAI_Biometric_Forecast_2026.csv",
        mime="text/csv"
    )
