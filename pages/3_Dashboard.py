import streamlit as st
import pandas as pd
import plotly.express as px
from engine.dashboard_engine import generate_kpis

# ---------------- Page Config ----------------
st.set_page_config(page_title="UIDAI Planning Dashboard", layout="wide")
st.title("📊 UIDAI Executive Planning Dashboard — 2026")

# ---------------- Load Data ----------------
df = pd.read_csv("output/forecast_2026.csv")

# ---------------- Sidebar ----------------
st.sidebar.header("🔎 Filters")

months = sorted(df["forecast_month"].unique().tolist())
selected_month = st.sidebar.selectbox("Select Forecast Month", ["All"] + months)

if selected_month != "All":
    df = df[df["forecast_month"] == selected_month]

# ---------------- KPIs ----------------
kpis = generate_kpis(df)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📦 Total Bio Load", kpis["total_load"])
col2.metric("📍 Peak Pincode", kpis["peak_pincode"])
col3.metric("🔥 Peak Month", kpis["peak_month"])
col4.metric("📊 Avg Monthly Load", kpis["avg_monthly_load"])
col5.metric("⚠ High Risk Zones", kpis["high_risk_pincodes"])

st.divider()

# ---------------- Charts ----------------

st.subheader("📈 Bio Load Forecast by Month")
monthly_chart = px.bar(
    df.groupby("forecast_month")["predicted_bio_load"].sum().reset_index(),
    x="forecast_month",
    y="predicted_bio_load",
    labels={"forecast_month": "Month", "predicted_bio_load": "Total Bio Load"}
)
st.plotly_chart(monthly_chart, use_container_width=True)

st.subheader("📍 Bio Load by Pincode")
pincode_chart = px.bar(
    df,
    x="pincode",
    y="predicted_bio_load",
    color="forecast_month",
    labels={"predicted_bio_load": "Bio Load"}
)
st.plotly_chart(pincode_chart, use_container_width=True)

st.subheader("⚠ Overload Risk Zones")
risk_df = df[df["overload_probability"] > 1]

if len(risk_df) == 0:
    st.success("No overload risk zones detected for selected period.")
else:
    st.dataframe(risk_df, use_container_width=True)

st.divider()

st.subheader("📄 Forecast Data Preview")
st.dataframe(df, use_container_width=True)
