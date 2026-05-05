import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, r2_score

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")

st.title("🔮 Demand Forecasting")
st.markdown("**Analyze historical trends and forecast FUTURE demand**")
st.markdown("---")


# Load sample data
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

# Sidebar controls
st.sidebar.markdown("### Forecasting Parameters")
forecast_months = st.sidebar.slider("Forecast months ahead", 1, 12, 6)

st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Historical Trends", "🔮 Future Forecast", "📊 Model Accuracy"])

with tab1:
    st.subheader("Historical Demand Patterns")
    st.markdown("*Data from Jan 2025 to Feb 2026*")

    # Aggregate data by month
    monthly_data = data.groupby('month')['bio_load'].agg(['sum', 'mean']).reset_index()
    monthly_data['date'] = pd.to_datetime(monthly_data['month'], format='%b-%Y')
    monthly_data = monthly_data.sort_values('date')

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
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

    fig.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['mean'],
        mode='lines',
        name='Average Load',
        line=dict(color='#ff9800', width=2, dash='dash'),
        hovertemplate='<b>%{x}</b><br>Average Load: %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title="Historical Demand (Jan 2025 - Feb 2026)",
        xaxis_title="Month",
        yaxis_title="Load Count",
        height=400,
        hovermode='x unified',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Load", f"{monthly_data['sum'].sum():,.0f}")
    with col2:
        st.metric("Peak Load", f"{monthly_data['sum'].max():,.0f}")
    with col3:
        st.metric("Lowest Load", f"{monthly_data['sum'].min():,.0f}")
    with col4:
        st.metric("Average Load", f"{monthly_data['sum'].mean():,.0f}")

with tab2:
    st.subheader(f"🔮 Future Forecast ({forecast_months} Months Ahead)")

    # Load historical data
    monthly_hist = data.groupby('month')['bio_load'].sum().reset_index()
    monthly_hist['date'] = pd.to_datetime(monthly_hist['month'], format='%b-%Y')
    monthly_hist = monthly_hist.sort_values('date')

    # Build model
    X = np.arange(len(monthly_hist)).reshape(-1, 1)
    y = monthly_hist['bio_load'].values

    model = LinearRegression()
    model.fit(X, y)

    # Get parameters
    slope = model.coef_[0]
    intercept = model.intercept_

    # Prevent negative predictions
    min_historical = monthly_hist['bio_load'].min()
    min_allowed = min_historical * 0.5

    if intercept < min_allowed:
        intercept = min_allowed

    if slope < -10:
        slope = -5

    # Predict future
    last_index = len(monthly_hist) - 1
    future_X = np.arange(last_index + 1, last_index + 1 + forecast_months)
    forecast_values = np.maximum(intercept + slope * future_X, min_allowed)

    # Create forecast table
    last_date = monthly_hist['date'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_months, freq='MS')

    forecast_table = pd.DataFrame({
        'month': [d.strftime('%b-%Y') for d in future_dates],
        'forecast': forecast_values.astype(int)
    })

    # Chart
    fig_forecast = go.Figure()

    fig_forecast.add_trace(go.Scatter(
        x=monthly_hist['month'],
        y=monthly_hist['bio_load'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Actual: %{y:,.0f}<extra></extra>'
    ))

    fig_forecast.add_trace(go.Scatter(
        x=forecast_table['month'],
        y=forecast_table['forecast'],
        mode='lines+markers',
        name='Forecast (Predicted)',
        line=dict(color='#ff6b6b', width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>Predicted: %{y:,.0f}<extra></extra>'
    ))

    fig_forecast.update_layout(
        title=f"Demand Forecast: History + {forecast_months} Month Prediction",
        xaxis_title="Month",
        yaxis_title="Load Count",
        height=450,
        hovermode='x unified',
        template='plotly_dark',
        legend=dict(x=0.02, y=0.98)
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    # Forecast table
    st.subheader("📋 Predicted Monthly Demand")

    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(forecast_table, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Model Configuration**")
        st.info(f"""
        Base Load: **{intercept:.0f}**

        Monthly Trend: **{slope:+.1f}**

        Min Safety Floor: **{min_allowed:.0f}**
        """)

    # Summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Historical Avg", f"{monthly_hist['bio_load'].mean():,.0f}")

    with col2:
        st.metric("Forecast Avg", f"{forecast_table['forecast'].mean():,.0f}")

    with col3:
        growth = ((forecast_table['forecast'].mean() - monthly_hist['bio_load'].mean()) / monthly_hist[
            'bio_load'].mean()) * 100
        st.metric("Expected Change", f"{growth:+.1f}%")

with tab3:
    st.subheader("📊 Model Accuracy & Validation")

    # Calculate metrics
    monthly_hist = data.groupby('month')['bio_load'].sum().reset_index()
    monthly_hist['date'] = pd.to_datetime(monthly_hist['month'], format='%b-%Y')
    monthly_hist = monthly_hist.sort_values('date')

    X = np.arange(len(monthly_hist)).reshape(-1, 1)
    y = monthly_hist['bio_load'].values

    model = LinearRegression()
    model.fit(X, y)

    # Predictions on historical data
    y_pred = model.predict(X)
    y_pred = np.maximum(y_pred, y.min() * 0.5)

    # Calculate metrics
    mape = mean_absolute_percentage_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    mae = np.mean(np.abs(y - y_pred))
    rmse = np.sqrt(np.mean((y - y_pred) ** 2))

    # Display metrics - FIXED (no delta with multiple values)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("R² Score", f"{r2:.3f}")
        st.caption("Higher is better (max 1.0)")

    with col2:
        st.metric("MAPE (%)", f"{mape:.1f}%")
        st.caption("Lower is better")

    with col3:
        st.metric("MAE", f"{mae:.0f}")
        st.caption("Mean absolute error")

    with col4:
        st.metric("RMSE", f"{rmse:.0f}")
        st.caption("Root mean squared error")

    st.markdown("---")

    # Validation chart
    st.markdown("### Model Performance: Actual vs Predicted")

    fig_validation = go.Figure()

    fig_validation.add_trace(go.Scatter(
        x=monthly_hist['month'],
        y=y,
        mode='lines+markers',
        name='Actual Data',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))

    fig_validation.add_trace(go.Scatter(
        x=monthly_hist['month'],
        y=y_pred,
        mode='lines',
        name='Model Fit',
        line=dict(color='#ff9800', width=2, dash='dash')
    ))

    fig_validation.update_layout(
        title="How Well Model Fits Historical Data",
        xaxis_title="Month",
        yaxis_title="Load Count",
        height=400,
        hovermode='x unified',
        template='plotly_dark'
    )

    st.plotly_chart(fig_validation, use_container_width=True)

    # Explanation
    st.markdown("### What These Metrics Mean")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **R² Score (0-1)**
        - 1.0 = Perfect fit
        - 0.87 = Very good
        - 0.5 = Moderate

        **MAPE (%)**
        - <10% = Excellent
        - 10-20% = Good
        - >20% = Poor
        """)

    with col2:
        st.markdown("""
        **MAE**
        - Average error amount
        - ±50 means typically off by 50

        **RMSE**
        - Penalizes large errors
        - Higher = bigger errors
        """)