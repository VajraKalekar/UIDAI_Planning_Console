import pandas as pd

def validate_and_clean(df):
    report = {}
    clean_df = df.copy()

    required_cols = ["pincode", "month", "age_0_5", "age_5_17", "age_18_greater"]

    missing_cols = [c for c in required_cols if c not in clean_df.columns]

    if missing_cols:
        report["status"] = "FAILED"
        report["missing_columns"] = missing_cols
        return None, report

    # Create bio_load column
    clean_df["bio_load"] = (
        clean_df["age_0_5"] +
        clean_df["age_5_17"] +
        clean_df["age_18_greater"]
    )

    # Convert month
    clean_df["month"] = pd.to_datetime(clean_df["month"])

    # Remove invalid rows
    before = len(clean_df)
    clean_df = clean_df.dropna()
    after = len(clean_df)

    report["status"] = "SUCCESS"
    report["rows_before"] = before
    report["rows_after"] = after
    report["rows_removed"] = before - after
    report["generated_column"] = "bio_load"

    clean_df = clean_df.sort_values(["pincode", "month"])

    return clean_df, report
