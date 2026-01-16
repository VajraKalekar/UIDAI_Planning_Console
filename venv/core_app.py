import streamlit as st

st.set_page_config(
    page_title="UIDAI Aadhaar-Seva Optimizer",
    layout="wide"
)

st.title("UIDAI Aadhaar-Seva Optimizer")
st.subheader("Dynamic Infrastructure Planning & Forecasting System")

st.markdown("""
### Welcome to UIDAI Planning Console

This platform enables UIDAI administrators to:

- Upload Aadhaar enrolment, demographic and biometric datasets  
- Analyze biometric infrastructure stress at PIN-code level  
- Forecast future demand using trend intelligence  
- Plan dynamic kit deployment  
- Generate early warnings and relocation plans  

Use the sidebar to navigate through modules.
""")

st.success("System Ready. Please use the sidebar to begin.")
