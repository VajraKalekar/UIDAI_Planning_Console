import pandas as pd
import numpy as np


# ---------- Time Series Builder ----------
def build_monthly_timeseries(df):
    df["month"] = pd.to_datetime(df["month"])

    monthly = (
        df.groupby(["pincode", "month"])["bio_load"]
        .sum()
        .reset_index()
        .sort_values(["pincode", "month"])
    )

    return monthly


# ---------- Forecast Model ----------
def forecast_2026(monthly_df):
    forecasts = []

    for pincode in monthly_df["pincode"].unique():
        data = monthly_df[monthly_df["pincode"] == pincode].copy()

        # Use last 3 months trend as predictor
        recent = data.tail(3)["bio_load"]

        if len(recent) < 3:
            predicted_load = recent.mean()
        else:
            growth = (recent.iloc[-1] - recent.iloc[0]) / 3
            predicted_load = recent.iloc[-1] + growth

        predicted_load = max(0, int(predicted_load))

        forecasts.append({
            "pincode": pincode,
            "forecast_month": "2026-02",
            "predicted_bio_load": predicted_load,
        })

    forecast_df = pd.DataFrame(forecasts)

    return forecast_df


# ---------- Kit Planning ----------
def build_kit_plan(forecast_df):
    KIT_CAPACITY = 50

    forecast_df["predicted_kits_required"] = (
            forecast_df["predicted_bio_load"] / KIT_CAPACITY
    ).apply(lambda x: int(x) + 1)

    forecast_df["overload_probability"] = (
            (forecast_df["predicted_bio_load"] / 500) * 100
    ).clip(0, 100).round(2)

    forecast_df["early_warning"] = np.where(
        forecast_df["predicted_bio_load"] > 400, "YES", "NO"
    )

    return forecast_df
