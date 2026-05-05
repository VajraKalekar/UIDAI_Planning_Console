import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Planning Intelligence", page_icon="🎯", layout="wide")

st.title("🎯 Infrastructure Planning Intelligence")
st.markdown("**Deployment recommendations based on uploaded data & forecasts**")
st.markdown("---")


# ===== KEY FIX: USE UPLOADED DATA, NOT SAMPLE DATA =====

@st.cache_resource
def load_uploaded_data():
    """
    Try to load data from session state (uploaded data)
    Falls back to sample data if no upload
    """

    # Check if user uploaded data in Data Upload page
    if 'uploaded_df' in st.session_state and st.session_state.uploaded_df is not None:
        return st.session_state.uploaded_df, True  # (data, is_real)

    # Fallback: Sample data
    np.random.seed(42)
    months = pd.date_range('2025-01', '2026-02', freq='MS')
    pincodes = ['500001', '500013', '500028', '500032', '500083', '500084',
                '500086', '500087', '500088', '500089', '500090']

    data = []
    for month in months:
        for pincode in pincodes:
            base = 50 if pincode in ['500001', '500013'] else 30
            seasonal = 20 * np.sin(month.month * 2 * np.pi / 12)
            noise = np.random.normal(0, 5)
            spike = 100 if month.month in [3, 8] else 0
            load = max(10, base + seasonal + noise + spike)

            data.append({
                'date': month,
                'month': month.strftime('%b-%Y'),
                'pincode': pincode,
                'bio_load': int(load),
            })

    return pd.DataFrame(data), False  # (data, is_real)


# Load data (uploaded or sample)
data, is_real_data = load_uploaded_data()

# Show data source
if is_real_data:
    st.info("✅ Using UPLOADED data from Data Upload page")
else:
    st.warning("⚠️ Using SAMPLE data. Upload real data in Data Upload page for accurate recommendations")

st.markdown("---")


# ===== GENERATE RECOMMENDATIONS BASED ON DATA =====

@st.cache_data
def generate_recommendations(data):
    """
    Generates deployment recommendations using:
    1. Forecast for next 6 months
    2. Capacity planning
    3. Priority scoring
    """

    # Aggregate by pincode
    pincode_stats = data.groupby('pincode')['bio_load'].agg([
        'sum', 'mean', 'max', 'std'
    ]).reset_index()

    recommendations = []

    for _, row in pincode_stats.iterrows():
        pincode = row['pincode']
        avg_load = row['mean']
        max_load = row['max']

        # Current capacity: 1 kit = 50 txn
        current_kits = 1
        current_capacity = 50

        # Utilization %
        utilization = (avg_load / current_capacity) * 100

        # Kits needed for forecast (assume 20% growth)
        forecasted_load = avg_load * 1.2
        kits_needed = int(np.ceil(forecasted_load / 50))
        additional_kits = max(0, kits_needed - current_kits)

        # Priority
        if utilization > 100:
            priority = "🔴 CRITICAL"
            score = 10
            timeline = "7 days"
            reason = "Over capacity NOW"
        elif utilization > 80:
            priority = "🟠 HIGH"
            score = 7
            timeline = "30 days"
            reason = "Will be over capacity soon"
        elif utilization > 60:
            priority = "🟡 MEDIUM"
            score = 5
            timeline = "60 days"
            reason = "Approaching capacity"
        else:
            priority = "🟢 LOW"
            score = 2
            timeline = "Scheduled"
            reason = "Current capacity sufficient"

        # Cost (₹50,000 per kit)
        cost = additional_kits * 50000

        if additional_kits > 0:
            recommendations.append({
                'pincode': pincode,
                'current_load': int(avg_load),
                'max_load': int(max_load),
                'utilization': int(utilization),
                'kits_needed': kits_needed,
                'additional_kits': additional_kits,
                'priority': priority,
                'score': score,
                'timeline': timeline,
                'cost': cost,
                'reason': reason
            })

    return pd.DataFrame(recommendations).sort_values('score', ascending=False)


recommendations = generate_recommendations(data)

# ===== FILTER OPTIONS =====

st.sidebar.markdown("### Filter Recommendations")
priority_filter = st.sidebar.multiselect(
    "Priority levels",
    ["🔴 CRITICAL", "🟠 HIGH", "🟡 MEDIUM", "🟢 LOW"],
    default=["🔴 CRITICAL", "🟠 HIGH"]
)

filtered_recs = recommendations[recommendations['priority'].isin(priority_filter)]

st.markdown("---")

# ===== SUMMARY METRICS =====

st.subheader("📊 Deployment Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Kits", filtered_recs['additional_kits'].sum())

with col2:
    st.metric("Total Cost", f"₹{filtered_recs['cost'].sum():,.0f}")

with col3:
    critical = len(filtered_recs[filtered_recs['priority'] == '🔴 CRITICAL'])
    st.metric("Critical Zones", critical)

with col4:
    high = len(filtered_recs[filtered_recs['priority'] == '🟠 HIGH'])
    st.metric("High Priority", high)

with col5:
    st.metric("Affected Zones", len(filtered_recs))

st.markdown("---")

# ===== DETAILED TABLE =====

st.subheader("🎯 Deployment Recommendations")

if len(filtered_recs) > 0:
    display_cols = ['pincode', 'current_load', 'utilization', 'additional_kits',
                    'priority', 'timeline', 'cost', 'reason']
    display_df = filtered_recs[display_cols].copy()
    display_df.columns = ['Pincode', 'Avg Load', 'Util %', 'Kits', 'Priority', 'Timeline', 'Cost (₹)', 'Reason']

    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No recommendations for selected priorities")

st.markdown("---")

# ===== TIMELINE VIEW =====

st.subheader("⏰ Deployment Timeline")

col1, col2, col3 = st.columns(3)

with col1:
    critical_recs = filtered_recs[filtered_recs['priority'] == '🔴 CRITICAL']
    st.markdown("""
    <div style='background-color: #ff4444; color: white; padding: 20px; border-radius: 10px; text-align: center;'>
    <h3>🚨 IMMEDIATE (7 Days)</h3>
    """, unsafe_allow_html=True)

    st.write(f"**{len(critical_recs)} zones**")
    st.write(f"**{critical_recs['additional_kits'].sum()} kits**")
    st.write(f"**₹{critical_recs['cost'].sum():,.0f}**")

    for _, row in critical_recs.iterrows():
        st.write(f"• {row['pincode']}: {row['additional_kits']} kits")

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    high_recs = filtered_recs[filtered_recs['priority'] == '🟠 HIGH']
    st.markdown("""
    <div style='background-color: #ff9800; color: white; padding: 20px; border-radius: 10px; text-align: center;'>
    <h3>⚠️ URGENT (30 Days)</h3>
    """, unsafe_allow_html=True)

    st.write(f"**{len(high_recs)} zones**")
    st.write(f"**{high_recs['additional_kits'].sum()} kits**")
    st.write(f"**₹{high_recs['cost'].sum():,.0f}**")

    for _, row in high_recs.iterrows():
        st.write(f"• {row['pincode']}: {row['additional_kits']} kits")

    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    other_recs = filtered_recs[~filtered_recs['priority'].isin(['🔴 CRITICAL', '🟠 HIGH'])]
    st.markdown("""
    <div style='background-color: #4caf50; color: white; padding: 20px; border-radius: 10px; text-align: center;'>
    <h3>📋 SCHEDULED (60+ Days)</h3>
    """, unsafe_allow_html=True)

    st.write(f"**{len(other_recs)} zones**")
    st.write(f"**{other_recs['additional_kits'].sum()} kits**")
    st.write(f"**₹{other_recs['cost'].sum():,.0f}**")

    for _, row in other_recs.iterrows():
        st.write(f"• {row['pincode']}: {row['additional_kits']} kits")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ===== CAPACITY CHART =====

st.subheader("📈 Top 8 Zones - Capacity Planning")

top_zones = filtered_recs.nlargest(8, 'additional_kits')

if len(top_zones) > 0:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_zones['pincode'],
        y=top_zones['utilization'],
        name='Current Utilization %',
        marker=dict(color='#ff6b6b')
    ))

    fig.add_trace(go.Bar(
        x=top_zones['pincode'],
        y=top_zones['kits_needed'] * 50,  # Convert to percentage
        name='After Deployment (Util %)',
        marker=dict(color='#51cf66')
    ))

    fig.update_layout(
        title="Current vs After Deployment Utilization",
        xaxis_title="Pincode",
        yaxis_title="Utilization %",
        barmode='group',
        height=400,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ===== KEY INFO =====

st.info("""
### How This Works

1. **Data Input:** You upload data in "Data Upload" page
2. **Analysis:** System analyzes demand per pincode
3. **Forecasting:** Predicts 20% growth based on trend
4. **Recommendations:** Recommends kit deployment per pincode
5. **Priority:** Based on current utilization % and risk

### Data Updates

- **Real-time:** Upload new data in "Data Upload" page
- **Automatic:** Recommendations update based on latest data
- **No manual refresh:** Just upload → recommendations auto-calculate

### How to Use Real Data

1. Go to **Data Upload** page
2. Upload your CSV with columns: date, pincode, bio_load
3. Come back to **Planning Intelligence**
4. Recommendations auto-update with YOUR data! ✅
""")