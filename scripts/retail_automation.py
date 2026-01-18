import pandas as pd
import numpy as np


def clean_retail_sales(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # Normalize common dirty placeholders
    df = df.replace(
        ["unknown", "UNKNOWN", "none", "NONE", "error", "", " "],
        np.nan
    )

    # Convert numeric columns safely
    numeric_cols = ["Price Per Unit", "Quantity", "Total Spent"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle missing numeric values
    df["Price Per Unit"] = df["Price Per Unit"].fillna(
        df["Price Per Unit"].median()
    )
    df["Quantity"] = df["Quantity"].fillna(
        df["Quantity"].median()
    )
    df["Total Spent"] = df["Total Spent"].fillna(0)

    # Apply retail validation rules
    df = df[(df["Price Per Unit"] > 0) & (df["Quantity"] > 0)]
    df["Quantity"] = df["Quantity"].astype(int)

    # Clean Discount Applied column
    df["Discount Applied"] = (
        df["Discount Applied"].fillna("no").astype(str).str.lower().str.strip().replace({
            "y": "yes",
            "true": "yes",
            "1": "yes",
            "false": "no",
            "0": "no"
        })
    )

    # Standardize categorical columns
    categorical_cols = ["Category", "Item", "Payment Method", "Location"]
    for col in categorical_cols:
        df[col] = (
            df[col]
            .fillna("unknown")
            .astype(str)
            .str.lower()
            .str.strip()
        )

    # Recalculate and fix Total Spent
    recalculated_total = df["Price Per Unit"] * df["Quantity"]
    df["Total Spent"] = np.where(
        df["Total Spent"] != recalculated_total,
        recalculated_total,
        df["Total Spent"]
    )

    # Parse and validate transaction date
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"],
        errors="coerce"
    )
    df = df.dropna(subset=["Transaction Date"])

    # Remove duplicate transactions
    df = df.drop_duplicates(subset="Transaction ID")

    # Save final clean dataset
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    clean_retail_sales(
        input_csv="retail_store_sales.csv",
        output_csv="retail_store_sales_clean.csv"
    )
