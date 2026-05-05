# FILE: pages/02_📤_Data_Upload.py
# PURPOSE: Frontend UI - Upload CSV and validate

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Data Upload", page_icon="📤", layout="wide")

st.title("📤 Data Upload & Validation")
st.markdown("Upload Aadhaar transaction data - will be used for recommendations")
st.markdown("---")

with st.expander("📋 Data Format Requirements"):
    st.info("""
    Your CSV should have columns like:
    - **Date:** date, month, transaction_date (any format)
    - **Location:** pincode, pin, location  
    - **Count:** bio_load, load, count, transactions

    System will auto-detect columns and validate data.
    Once uploaded, Planning Intelligence will use this data!
    """)

st.subheader("📁 Upload Data File")
uploaded_file = st.file_uploader("Select CSV file", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ File loaded: {len(df):,} records, {len(df.columns)} columns")

        # ===== DETECT COLUMNS =====

        date_col = None
        pincode_col = None
        load_col = None

        for col in df.columns:
            col_lower = col.lower()
            if 'date' in col_lower or 'month' in col_lower:
                date_col = col
            elif 'pin' in col_lower or 'location' in col_lower:
                pincode_col = col
            elif 'load' in col_lower or 'count' in col_lower or 'bio' in col_lower:
                load_col = col

        # ===== VALIDATION =====

        st.subheader("✓ Data Validation")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Detected Columns:**")
            if date_col:
                st.success(f"✅ Date: **{date_col}**")
            else:
                st.error("❌ Date column not found")

            if pincode_col:
                st.success(f"✅ Pincode: **{pincode_col}**")
            else:
                st.error("❌ Pincode column not found")

            if load_col:
                st.success(f"✅ Load: **{load_col}**")
            else:
                st.warning("⚠️ Load column not found")

        with col2:
            st.markdown("**Data Quality:**")

            missing = df.isnull().sum().sum()
            duplicates = df.duplicated().sum()

            if missing == 0:
                st.success("✅ No missing values")
            else:
                st.warning(f"⚠️ {missing} missing values")

            if duplicates == 0:
                st.success("✅ No duplicates")
            else:
                st.warning(f"⚠️ {duplicates} duplicates")

            st.info(f"📊 Total columns: {len(df.columns)}")

        st.markdown("---")

        # ===== DATA PREVIEW =====

        st.subheader("👁️ Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("---")

        # ===== STATISTICS =====

        st.subheader("📊 Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Records", f"{len(df):,}")
            st.metric("Total Columns", len(df.columns))

            if pincode_col:
                st.metric("Unique Pincodes", df[pincode_col].nunique())

        with col2:
            if date_col:
                try:
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    date_min = df_temp[date_col].min()
                    date_max = df_temp[date_col].max()
                    st.metric("Date Range", f"{date_min.strftime('%b-%Y')} to {date_max.strftime('%b-%Y')}")
                except:
                    st.info("Could not parse dates")

        st.markdown("---")

        # ===== SAVE TO SESSION STATE =====
        # This is KEY! Saves data so Planning Intelligence can use it

        st.subheader("💾 Save Data for Planning Intelligence")

        if st.button("✅ Save & Use This Data"):
            # Save to Streamlit session state
            st.session_state.uploaded_df = df
            st.session_state.upload_date = datetime.now()

            st.success("""
            ✅ **Data Saved Successfully!**

            Your data is now available to:
            - Planning Intelligence (recommendations)
            - Forecasting (predictions)

            Go to those pages to see analysis based on YOUR data!
            """)

        st.markdown("---")

        # ===== DOWNLOAD OPTION =====

        st.subheader("⬇️ Download Data")

        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"data_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

        # Show current status
        if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
            upload_time = st.session_state.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            st.info(f"""
            ### Current Data Status

            ✅ **Data Active:** {len(st.session_state.uploaded_df):,} records loaded

            **Last Updated:** {upload_time}

            Planning Intelligence is using THIS data for recommendations!
            """)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Make sure it's a valid CSV file")

else:
    # Show status if data already loaded
    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        st.success(f"""
        ### ✅ Data Currently Active

        Records: {len(st.session_state.uploaded_df):,}
        Last Updated: {st.session_state.upload_date.strftime('%Y-%m-%d %H:%M:%S')}

        Planning Intelligence is using this data.

        **Upload new data above to refresh.**
        """)
    else:
        st.info("👈 Upload a CSV to start")