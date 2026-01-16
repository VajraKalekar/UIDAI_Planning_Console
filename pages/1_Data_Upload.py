import streamlit as st
import pandas as pd
from engine.engine.data_validator import validate_and_clean

st.set_page_config(page_title="UIDAI Planning Console", layout="wide")

st.title("📥 UIDAI Data Upload Portal")
st.write("Upload monthly UIDAI district or pincode load data for validation and forecasting.")

uploaded_file = st.file_uploader("Upload Monthly Load CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True)

    if st.button("✅ Validate & Clean Data"):

        with st.spinner("Validating dataset..."):
            clean_df, report = validate_and_clean(df)

        st.subheader("📊 Validation Report")
        st.json(report)

        if clean_df is not None:
            st.subheader("🧹 Clean Data Preview")
            st.dataframe(clean_df.head(20), use_container_width=True)

            # Save output for next pipeline stage
            clean_df.to_csv("output/clean_monthly_load.csv", index=False)

            st.success("Clean dataset saved to: output/clean_monthly_load.csv")
            st.info("Dataset is now ready for Forecast Engine.")
