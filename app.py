import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="UIDAI Planning Console",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .critical-alert {
        background-color: #ff4444;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-alert {
        background-color: #ff9800;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #4caf50;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("🏛️ UIDAI Executive Planning Dashboard — 2026")
st.markdown("**Data-Driven Capacity Planning & Operational Forecasting Console**")
st.markdown("---")

# Sidebar
st.sidebar.markdown("## Navigation")
st.sidebar.markdown("Use the pages in the sidebar to explore:")
st.sidebar.markdown("""
- 📊 **Executive Summary** - KPIs and critical alerts
- 📤 **Data Upload & Validation** - Manage input data
- 🔮 **Demand Forecasting** - View forecasts and trends
- 🎯 **Planning Intelligence** - Deployment recommendations
- 📈 **Advanced Analytics** - Scenario analysis
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### About This Project")
st.sidebar.info("""
This DSS transforms Aadhaar operational data into actionable intelligence for:
- Infrastructure deployment planning
- Capacity utilization optimization
- Risk identification & mitigation
- Manpower allocation

**Status:** Active | **Last Updated:** 2026-02-15
""")


# Load or create sample data
@st.cache_resource
def load_sample_data():
    """Generate realistic sample Aadhaar data"""
    np.random.seed(42)

    # Create sample monthly demand data
    months = pd.date_range('2025-01', '2026-02', freq='MS')
    pincodes = ['500001', '500013', '500028', '500032', '500083', '500084',
                '500086', '500087', '500088', '500089', '500090']

    # Generate realistic demand patterns
    data = []
    for month in months:
        for pincode in pincodes:
            # Base load with seasonal variation and some pincodes more active
            base = 50 if pincode in ['500001', '500013'] else 30
            seasonal = 20 * np.sin(month.month * 2 * np.pi / 12)
            noise = np.random.normal(0, 5)
            spike = 100 if month.month in [3, 8] else 0  # Welfare drives

            load = max(10, base + seasonal + noise + spike)

            data.append({
                'date': month,
                'month': month.strftime('%b-%Y'),
                'pincode': pincode,
                'bio_load': int(load),
                'age_group_5_17': int(load * 0.3),
                'age_group_18_plus': int(load * 0.7),
                'enrolment': int(load * 0.4),
                'biometric_update': int(load * 0.3),
                'demographic_update': int(load * 0.3)
            })

    return pd.DataFrame(data)


@st.cache_data
def load_uploaded_data(uploaded_file):
    """Load and cache uploaded data"""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            return df, None
        except Exception as e:
            return None, str(e)
    return None, None


@st.cache_data
def calculate_risk_zones(data):
    """Calculate risk zones based on load patterns"""
    risk_data = []

    pincode_stats = data.groupby('pincode').agg({
        'bio_load': ['sum', 'mean', 'max']
    }).reset_index()

    pincode_stats.columns = ['pincode', 'total_load', 'avg_load', 'max_load']

    # Risk scoring
    for _, row in pincode_stats.iterrows():
        if row['max_load'] > 150:
            risk_level = 'CRITICAL'
            risk_score = 9
        elif row['max_load'] > 100:
            risk_level = 'HIGH'
            risk_score = 7
        elif row['max_load'] > 60:
            risk_level = 'MEDIUM'
            risk_score = 5
        else:
            risk_level = 'LOW'
            risk_score = 2

        # Estimate capacity needs (assuming 50 transactions/kit/day)
        kits_needed = int(row['avg_load'] / 50) + 1

        risk_data.append({
            'pincode': row['pincode'],
            'total_load': int(row['total_load']),
            'avg_load': int(row['avg_load']),
            'max_load': int(row['max_load']),
            'risk_level': risk_level,
            'risk_score': risk_score,
            'kits_needed': kits_needed,
            'utilization_pct': int((row['avg_load'] / 50) * 100)
        })

    return pd.DataFrame(risk_data).sort_values('risk_score', ascending=False)


# Main Dashboard Content
col1, col2, col3, col4, col5 = st.columns(5)

# Load data
data = load_sample_data()

# Calculate KPIs
total_bio_load = data['bio_load'].sum()
peak_pincode = data.groupby('pincode')['bio_load'].sum().idxmax()
peak_pincode_load = data.groupby('pincode')['bio_load'].sum().max()
peak_month = data.groupby('month')['bio_load'].sum().idxmax()
high_risk_count = len(calculate_risk_zones(data)[calculate_risk_zones(data)['risk_level'].isin(['CRITICAL', 'HIGH'])])

# Display KPI Cards
with col1:
    st.metric(
        "📊 Total Bio Load",
        f"{total_bio_load:,}",
        delta="Operational baseline"
    )

with col2:
    st.metric(
        "📍 Peak Pincode",
        peak_pincode,
        delta=f"{peak_pincode_load} max load"
    )

with col3:
    st.metric(
        "📅 Peak Month",
        peak_month,
        delta="2026-02"
    )

with col4:
    st.metric(
        "⚙️ Avg Monthly Load",
        f"{data['bio_load'].sum() // len(data['month'].unique()):,}",
        delta="Per month"
    )

with col5:
    st.metric(
        "🚨 High-Risk Zones",
        high_risk_count,
        delta="Zones above threshold"
    )

st.markdown("---")

# Create tabs for different analysis views
tab1, tab2, tab3 = st.tabs(["📈 Demand Trends", "⚠️ Risk Analysis", "🎯 Recommendations"])

with tab1:
    st.subheader("Biometric Load Forecast by Month")
    st.markdown("*Monthly demand aggregation across all pincodes with trend analysis*")

    # Aggregate data by month
    monthly_data = data.groupby('month')['bio_load'].agg(['sum', 'mean', 'std']).reset_index()
    monthly_data['date'] = pd.to_datetime(monthly_data['month'], format='%b-%Y')
    monthly_data = monthly_data.sort_values('date')

    # Create interactive line chart
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['sum'],
        mode='lines+markers',
        name='Total Load',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='<b>%{x}</b><br>Total Load: %{y:,.0f}<extra></extra>'
    ))

    fig_trend.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['mean'],
        mode='lines',
        name='Avg Load',
        line=dict(color='#ff9800', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Avg Load: %{y:,.0f}<extra></extra>'
    ))

    fig_trend.update_layout(
        title="Monthly Biometric Load Trend (2025-2026)",
        xaxis_title="Month",
        yaxis_title="Load Count",
        height=400,
        hovermode='x unified',
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig_trend, use_container_width=True)

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"📊 **Total Load**: {monthly_data['sum'].sum():,.0f}")
    with col2:
        st.success(f"📈 **Peak Month**: {monthly_data['sum'].max():,.0f}")
    with col3:
        st.warning(f"📉 **Low Month**: {monthly_data['sum'].min():,.0f}")
    with col4:
        st.info(f"📊 **Avg Month**: {monthly_data['sum'].mean():,.0f}")

with tab2:
    st.subheader("Load Distribution by Pincode")
    st.markdown("*Identifying high-load and at-risk service locations*")

    # Pincode analysis
    pincode_data = data.groupby('pincode').agg({
        'bio_load': ['sum', 'mean', 'max']
    }).reset_index()
    pincode_data.columns = ['pincode', 'total_load', 'avg_load', 'max_load']
    pincode_data = pincode_data.sort_values('total_load', ascending=True)

    # Horizontal bar chart
    fig_pincode = px.bar(
        pincode_data,
        y='pincode',
        x='total_load',
        orientation='h',
        title='Biometric Load by Pincode (Ranked)',
        labels={'total_load': 'Total Load', 'pincode': 'Pincode'},
        color='total_load',
        color_continuous_scale='RdYlGn_r',
        height=400
    )

    fig_pincode.update_layout(
        template='plotly_dark',
        hovermode='y unified',
        margin=dict(l=0, r=0, t=40, b=0)
    )

    st.plotly_chart(fig_pincode, use_container_width=True)

    # Risk zones table
    st.subheader("⚠️ Overload Risk Assessment")
    risk_zones = calculate_risk_zones(data)


    # Color code the risk level
    def style_risk_level(val):
        if val == 'CRITICAL':
            return '🔴 CRITICAL'
        elif val == 'HIGH':
            return '🟠 HIGH'
        elif val == 'MEDIUM':
            return '🟡 MEDIUM'
        else:
            return '🟢 LOW'


    risk_display = risk_zones.copy()
    risk_display['risk_level'] = risk_display['risk_level'].apply(style_risk_level)
    risk_display = risk_display.rename(columns={
        'pincode': 'Pincode',
        'total_load': 'Total Load',
        'avg_load': 'Avg Load',
        'max_load': 'Peak Load',
        'risk_level': 'Risk Level',
        'utilization_pct': 'Utilization %',
        'kits_needed': 'Kits Needed'
    })

    st.dataframe(
        risk_display[['Pincode', 'Total Load', 'Avg Load', 'Peak Load', 'Risk Level', 'Utilization %', 'Kits Needed']],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("🎯 Infrastructure Deployment Recommendations")
    st.markdown("*Prioritized deployment plan based on demand forecasting and risk analysis*")

    risk_zones = calculate_risk_zones(data)

    # Filter high and critical risk zones
    deployment_zones = risk_zones[risk_zones['risk_level'].isin(['CRITICAL', 'HIGH'])].copy()

    if len(deployment_zones) > 0:
        # Priority scoring
        deployment_zones['priority_score'] = (
                deployment_zones['risk_score'] * 0.4 +
                (deployment_zones['max_load'] / deployment_zones['max_load'].max() * 10) * 0.3 +
                (deployment_zones['utilization_pct'] / 100 * 10) * 0.3
        ).astype(int)

        deployment_zones = deployment_zones.sort_values('priority_score', ascending=False).reset_index(drop=True)
        deployment_zones['rank'] = range(1, len(deployment_zones) + 1)

        # Create recommendations table
        recommendations = deployment_zones[[
            'rank', 'pincode', 'utilization_pct', 'kits_needed', 'risk_level', 'priority_score'
        ]].copy()

        recommendations.columns = ['Priority Rank', 'Pincode', 'Utilization %', 'Kits to Deploy', 'Risk Level', 'Score']

        # Display with color coding
        st.dataframe(recommendations, use_container_width=True, hide_index=True)

        # Recommendations details
        st.markdown("### Deployment Timeline")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='critical-alert'><b>🚨 CRITICAL (Deploy Immediately)</b><br>Within 7-14 days</div>",
                        unsafe_allow_html=True)
            critical = deployment_zones[deployment_zones['risk_level'] == 'CRITICAL']
            for _, row in critical.iterrows():
                st.write(
                    f"**{row['pincode']}**: Deploy {row['kits_needed']} kits (Utilization: {row['utilization_pct']}%)")

        with col2:
            st.markdown("<div class='warning-alert'><b>⚠️ HIGH (Deploy Soon)</b><br>Within 15-30 days</div>",
                        unsafe_allow_html=True)
            high = deployment_zones[deployment_zones['risk_level'] == 'HIGH']
            for _, row in high.iterrows():
                st.write(
                    f"**{row['pincode']}**: Deploy {row['kits_needed']} kits (Utilization: {row['utilization_pct']}%)")

        # Summary statistics
        st.markdown("### Deployment Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            total_kits = deployment_zones['kits_needed'].sum()
            st.metric("Total Kits to Deploy", total_kits)

        with col2:
            avg_utilization = deployment_zones['utilization_pct'].mean()
            st.metric("Avg Utilization (At-Risk)", f"{avg_utilization:.0f}%")

        with col3:
            critical_count = len(critical)
            st.metric("Critical Zones", critical_count)

        # Capacity planning estimate
        st.markdown("### Capacity Planning")
        cost_per_kit = 50000  # Estimated cost in INR
        total_cost = total_kits * cost_per_kit

        st.info(f"""
        **Estimated Deployment Cost**: ₹{total_cost:,.0f}
        - Number of kits: {total_kits}
        - Cost per kit: ₹{cost_per_kit:,.0f}
        - Deployment zones: {len(deployment_zones)}
        - Timeline: 30-60 days for full rollout
        """)
    else:
        st.success("✅ No critical deployment needs identified at this moment.")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>UIDAI Executive Planning Dashboard v1.0 | Data as of 2026-02-15</p>
    <p>For support or feedback, contact: <code>planning@uidai.gov.in</code></p>
</div>
""", unsafe_allow_html=True)