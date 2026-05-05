# FILE: engine/data_validator.py
# PURPOSE: Backend validation - detects columns, validates data, aggregates by month

import pandas as pd
import numpy as np


def detect_columns(df):
    """
    Automatically detect date, pincode, and load columns
    Works with any column naming convention
    """

    date_column = None
    pincode_column = None
    load_column = None

    # Look for date column
    date_keywords = ['date', 'month', 'transaction_date', 'Date', 'Month', 'MONTH']
    for col in df.columns:
        if col in date_keywords or 'date' in col.lower() or 'month' in col.lower():
            date_column = col
            break

    # Look for pincode column
    pincode_keywords = ['pincode', 'pin', 'location', 'Pincode', 'PIN', 'Location']
    for col in df.columns:
        if col in pincode_keywords or 'pin' in col.lower() or 'location' in col.lower():
            pincode_column = col
            break

    # Look for load/count column
    load_keywords = ['bio_load', 'load', 'count', 'transactions', 'bio_count', 'biometric_load']
    for col in df.columns:
        if col in load_keywords or 'load' in col.lower() or 'count' in col.lower() or 'bio' in col.lower():
            load_column = col
            break

    return date_column, pincode_column, load_column


def validate_data(df, date_column, pincode_column, load_column):
    """
    Validates data quality
    Returns: (is_valid, messages)
    """

    messages = []
    is_valid = True

    # Check if columns exist
    if date_column is None:
        messages.append("❌ Date column not found")
        is_valid = False
    else:
        messages.append(f"✅ Date column: {date_column}")

    if pincode_column is None:
        messages.append("❌ Pincode column not found")
        is_valid = False
    else:
        messages.append(f"✅ Pincode column: {pincode_column}")

    if load_column is None:
        messages.append("⚠️ Load column not found - will count records")
    else:
        messages.append(f"✅ Load column: {load_column}")

    # Check for duplicates
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        messages.append(f"⚠️ Duplicate rows: {duplicates}")
    else:
        messages.append("✅ No duplicates")

    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        messages.append(f"⚠️ Missing values: {missing}")
    else:
        messages.append("✅ No missing values")

    # Check for negative values if load column exists
    if load_column and (df[load_column] < 0).any():
        messages.append(f"❌ Negative values in {load_column}")
        is_valid = False
    elif load_column:
        messages.append("✅ No negative values")

    return is_valid, messages


def parse_dates(df, date_column):
    """
    Converts date column to datetime format
    Tries multiple date formats
    """

    df_copy = df.copy()

    date_formats = [
        '%Y-%m-%d',  # 2025-01-06
        '%d-%m-%Y',  # 06-01-2025
        '%m-%Y',  # 01-2025
        '%m/%Y',  # 01/2025
        '%Y-%m',  # 2025-01
        '%d/%m/%Y',  # 06/01/2025
    ]

    parsed = None
    for fmt in date_formats:
        try:
            parsed = pd.to_datetime(df_copy[date_column], format=fmt)
            break
        except:
            continue

    if parsed is None:
        try:
            parsed = pd.to_datetime(df_copy[date_column])
        except:
            return None

    df_copy[date_column] = parsed
    return df_copy


def get_statistics(df, date_column, pincode_column, load_column):
    """
    Calculate data statistics
    Returns: dictionary with stats
    """

    stats = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'unique_pincodes': df[pincode_column].nunique() if pincode_column else 0,
    }

    # Date range
    if date_column:
        try:
            df_temp = df.copy()
            df_temp[date_column] = pd.to_datetime(df_temp[date_column], errors='coerce')
            stats['date_min'] = df_temp[date_column].min()
            stats['date_max'] = df_temp[date_column].max()
        except:
            stats['date_min'] = None
            stats['date_max'] = None

    # Top pincodes
    if pincode_column and load_column:
        try:
            stats['top_pincodes'] = df.groupby(pincode_column)[load_column].sum().nlargest(5)
        except:
            stats['top_pincodes'] = None
    elif pincode_column:
        try:
            stats['top_pincodes'] = df[pincode_column].value_counts().head(5)
        except:
            stats['top_pincodes'] = None

    return stats