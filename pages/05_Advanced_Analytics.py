import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.cluster import KMeans

st.set_page_config(page_title="Advanced Analytics", page_icon="📈", layout="wide")

st.title("📈 Advanced Analytics")
st.markdown("Scenario planning, clustering, and deep insights")
st.markdown("---")


# Load data
@st.cache_resource
def load_data():
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

    return pd.DataFrame(data)


data = load_data()

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Scenario Planning", "🔀 Clustering Analysis", "📊 Correlation"])

with tab1:
    st.subheader("Scenario Planning: What-If Analysis")
    st.markdown("How will forecasts change under different scenarios?")

    col1, col2 = st.columns(2)

    with col1:
        scenario = st.selectbox(
            "Select scenario",
            [
                "Normal Growth (8% per month)",
                "Welfare Drive (3x demand in March)",
                "Policy Rollout (2x demand in Q2)",
                "Recession (-5% per month)"
            ]
        )

    with col2:
        impact = st.slider("Impact severity", 0.5, 2.0, 1.0, 0.1)

    # Calculate scenario data
    monthly_agg = data.groupby('month')['bio_load'].sum().reset_index()
    monthly_agg['date'] = pd.to_datetime(monthly_agg['month'], format='%b-%Y')
    monthly_agg = monthly_agg.sort_values('date')

    scenario_data = monthly_agg.copy()

    if "Welfare" in scenario:
        scenario_data.loc[scenario_data['month'] == 'Mar-2025', 'bio_load'] *= 3
    elif "Policy" in scenario:
        scenario_data.loc[scenario_data['month'].isin(['Apr-2025', 'May-2025']), 'bio_load'] *= 2
    elif "Recession" in scenario:
        scenario_data['bio_load'] = scenario_data['bio_load'] * (0.95 ** range(len(scenario_data)))

    scenario_data['bio_load'] = scenario_data['bio_load'] * impact

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly_agg['month'],
        y=monthly_agg['bio_load'],
        name='Base Case',
        line=dict(color='#667eea', width=2, dash='solid'),
        mode='lines+markers'
    ))

    fig.add_trace(go.Scatter(
        x=scenario_data['month'],
        y=scenario_data['bio_load'],
        name=scenario,
        line=dict(color='#ff9800', width=2, dash='dash'),
        mode='lines+markers'
    ))

    fig.update_layout(
        title=f"Scenario Analysis: {scenario}",
        xaxis_title="Month",
        yaxis_title="Load Count",
        height=400,
        template='plotly_dark',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Impact summary
    base_total = monthly_agg['bio_load'].sum()
    scenario_total = scenario_data['bio_load'].sum()
    impact_pct = ((scenario_total - base_total) / base_total) * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base Case Total", f"{base_total:,.0f}")
    with col2:
        st.metric("Scenario Total", f"{scenario_total:,.0f}")
    with col3:
        st.metric("Impact", f"{impact_pct:+.1f}%")

with tab2:
    st.subheader("Demand Clustering: Grouping Similar Pincodes")
    st.markdown("Which pincodes behave similarly?")

    # Prepare data for clustering
    pincode_features = data.groupby('pincode')['bio_load'].agg([
        'sum', 'mean', 'std', 'min', 'max'
    ]).reset_index()

    # Normalize
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(pincode_features[['sum', 'mean', 'std']])

    # K-means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    pincode_features['cluster'] = kmeans.fit_predict(features_scaled)

    # Visualization
    fig_cluster = px.scatter(
        pincode_features,
        x='mean',
        y='sum',
        size='std',
        color='cluster',
        hover_data=['pincode'],
        title="Pincode Clustering: Load Characteristics",
        labels={
            'mean': 'Average Load',
            'sum': 'Total Load',
            'std': 'Volatility'
        }
    )

    fig_cluster.update_layout(
        height=400,
        template='plotly_dark',
        colorscale='Blues'
    )

    st.plotly_chart(fig_cluster, use_container_width=True)

    # Cluster details
    st.markdown("### Cluster Characteristics")

    for cluster_id in sorted(pincode_features['cluster'].unique()):
        cluster_pincodes = pincode_features[pincode_features['cluster'] == cluster_id]

        with st.expander(f"Cluster {cluster_id + 1} ({len(cluster_pincodes)} pincodes)"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Avg Load",
                    f"{cluster_pincodes['mean'].mean():.0f}",
                    delta=f"σ={cluster_pincodes['std'].mean():.0f}"
                )

            with col2:
                st.metric(
                    "Total Load",
                    f"{cluster_pincodes['sum'].sum():,.0f}"
                )

            with col3:
                st.metric(
                    "Pincodes",
                    len(cluster_pincodes)
                )

            st.write("**Pincodes in this cluster:**")
            st.write(", ".join(cluster_pincodes['pincode'].values))

with tab3:
    st.subheader("Correlation Analysis")
    st.markdown("Relationship between different factors")

    # Create correlation data
    corr_data = data.pivot_table(
        index='month',
        columns='pincode',
        values='bio_load'
    ).fillna(method='ffill')

    # Correlation matrix
    corr_matrix = corr_data.corr()

    # Heatmap
    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmid=0
        )
    )

    fig_heatmap.update_layout(
        title="Pincode Demand Correlation",
        xaxis_title="Pincode",
        yaxis_title="Pincode",
        height=500,
        width=600
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Insights
    st.markdown("### Insights")
    st.info("""
    **High Correlation (>0.7):** Pincodes with similar demand patterns
    - May share customer base
    - Respond to same events
    - Benefit from shared resources

    **Low Correlation (<0.3):** Pincodes with different patterns
    - Serve different populations
    - Independent demand drivers
    - Need separate planning
    """)
