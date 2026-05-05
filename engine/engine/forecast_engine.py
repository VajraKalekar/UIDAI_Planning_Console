import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_demand_future_months(historical_data, forecast_months=6):
    """
    Creates demand forecast for FUTURE months (Mar-Aug 2026)

    Input: historical data (Jan 2025 - Feb 2026)
    Output: Predictions for Mar 2026 - Aug 2026 (and beyond)
    """

    # Step 1: Aggregate historical data by month
    monthly_data = historical_data.groupby('month')['bio_load'].sum().reset_index()
    monthly_data['date'] = pd.to_datetime(monthly_data['month'], format='%b-%Y')
    monthly_data = monthly_data.sort_values('date')

    print(f"Historical data points: {len(monthly_data)}")
    print(f"From: {monthly_data['date'].min().strftime('%b-%Y')}")
    print(f"To: {monthly_data['date'].max().strftime('%b-%Y')}")

    # Step 2: Prepare data for model
    X = np.arange(len(monthly_data)).reshape(-1, 1)  # [0,1,2,...,13]
    y = monthly_data['bio_load'].values  # [5200, 5100, 5400, ...]

    # Step 3: Build forecasting model
    model = LinearRegression()
    model.fit(X, y)

    # Get trend
    slope = model.coef_[0]
    intercept = model.intercept_

    print(f"\nModel learned:")
    print(f"  Base load: {intercept:.0f}")
    print(f"  Trend: +{slope:.0f} per month")

    # Step 4: PREDICT FUTURE MONTHS ← KEY PART!
    # If we have 14 months (0-13), next month is 14, then 15, 16...
    last_month_index = len(monthly_data) - 1  # 13 (Feb 2026)

    future_X = np.arange(last_month_index + 1, last_month_index + 1 + forecast_months).reshape(-1, 1)
    # future_X = [[14], [15], [16], [17], [18], [19]] ← Next 6 months!

    forecast_values = model.predict(future_X)
    # forecast_values = [5300, 5400, 5500, 5600, 5700, 5800] ← PREDICTIONS!

    # Step 5: Create forecast dates
    last_date = monthly_data['date'].max()
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_months, freq='MS')

    # Step 6: Create forecast dataframe
    forecast_df = pd.DataFrame({
        'month': [d.strftime('%b-%Y') for d in future_dates],
        'date': future_dates,
        'forecast': forecast_values.astype(int)
    })

    print(f"\nForecast generated:")
    print(f"  For {forecast_months} months")
    print(f"  From: {forecast_df['date'].min().strftime('%b-%Y')}")
    print(f"  To: {forecast_df['date'].max().strftime('%b-%Y')}")
    print(f"\nForecast values:")
    for _, row in forecast_df.iterrows():
        print(f"  {row['month']}: {row['forecast']}")

    return forecast_df, model, monthly_data


def create_combined_chart_data(historical_data, forecast_df):
    """
    Combines historical and forecast data for charting
    Shows solid line (past) + dashed line (future)
    """

    # Monthly historical
    monthly_hist = historical_data.groupby('month')['bio_load'].sum().reset_index()
    monthly_hist['date'] = pd.to_datetime(monthly_hist['month'], format='%b-%Y')
    monthly_hist = monthly_hist.sort_values('date')

    # Combine for charting
    combined = pd.DataFrame({
        'month': list(monthly_hist['month']) + list(forecast_df['month']),
        'load': list(monthly_hist['bio_load']) + list(forecast_df['forecast']),
        'type': ['Historical'] * len(monthly_hist) + ['Forecast'] * len(forecast_df)
    })

    return combined


# EXAMPLE USAGE:
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    months = pd.date_range('2025-01', '2026-02', freq='MS')
    pincodes = ['500001', '500013', '500028', '500032']

    data = []
    for month in months:
        for pincode in pincodes:
            base = 50 if pincode in ['500001', '500013'] else 30
            seasonal = 20 * np.sin(month.month * 2 * np.pi / 12)
            noise = np.random.normal(0, 5)
            spike = 100 if month.month in [3, 8] else 0
            load = max(10, base + seasonal + noise + spike)

            data.append({
                'month': month.strftime('%b-%Y'),
                'pincode': pincode,
                'bio_load': int(load)
            })

    historical_data = pd.DataFrame(data)

    # RUN FORECASTING
    print("=" * 60)
    print("FORECASTING DEMONSTRATION")
    print("=" * 60)

    forecast_df, model, monthly_hist = forecast_demand_future_months(
        historical_data,
        forecast_months=6  # Predict 6 months (Mar-Aug 2026)
    )

    print("\n" + "=" * 60)
    print("COMBINED DATA FOR CHART")
    print("=" * 60)
    combined = create_combined_chart_data(historical_data, forecast_df)
    print(combined)