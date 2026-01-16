import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("📂 UIDAI Data Upload & Processing Engine")

st.markdown("""
Upload Aadhaar operational datasets for analysis & forecasting.
Accepted format: CSV only.
""")

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Upload Section
col1, col2, col3 = st.columns(3)

with col1:
    enrolment_file = st.file_uploader("Upload Enrolment Data", type=["csv"])

with col2:
    biometric_file = st.file_uploader("Upload Biometric Data", type=["csv"])

with col3:
    demographic_file = st.file_uploader("Upload Demographic Data", type=["csv"])

def save_file(file, filename):
    with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as f:
        f.write(file.getbuffer())

# Save Files
if st.button("Save Uploaded Files"):
    if enrolment_file and biometric_file and demographic_file:
        save_file(enrolment_file, "enrolment.csv")
        save_file(biometric_file, "biometric.csv")
        save_file(demographic_file, "demographic.csv")

        st.success("All files uploaded successfully.")
    else:
        st.warning("Please upload all three datasets.")

# Preview Section
st.divider()
st.subheader("Preview Uploaded Data")

try:
    if os.path.exists(f"{UPLOAD_FOLDER}/enrolment.csv"):
        df = pd.read_csv(f"{UPLOAD_FOLDER}/enrolment.csv")
        st.write("Enrolment Data Preview")
        st.dataframe(df.head())
except:
    pass
