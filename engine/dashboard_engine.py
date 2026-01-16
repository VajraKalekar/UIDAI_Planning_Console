import pandas as pd

def generate_kpis(df: pd.DataFrame):
    kpis = {}

    # Total predicted bio load
    kpis["total_load"] = int(df["predicted_bio_load"].sum())

    # Peak load row
    peak_row = df.loc[df["predicted_bio_load"].idxmax()]

    kpis["peak_pincode"] = str(peak_row["pincode"])
    kpis["peak_month"] = str(peak_row["forecast_month"])
    kpis["peak_load"] = int(peak_row["predicted_bio_load"])

    # Average monthly load
    monthly_avg = df.groupby("forecast_month")["predicted_bio_load"].sum().mean()
    kpis["avg_monthly_load"] = int(monthly_avg)

    # High risk zones
    high_risk = df[df["overload_probability"] > 1]
    kpis["high_risk_pincodes"] = len(high_risk)

    return kpis
