import pandas as pd

def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = []

    # 1. Row count is not zero
    if len(df) == 0:
        errors.append("DataFrame is empty")

    # 2. Required columns exist
    required = ["order_id", "order_date", "ship_date", "customer_id",
                "product_id", "sales", "quantity", "profit"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        raise ValueError(errors)  # stop early, other checks need these

    # 3. No nulls in key columns
    nulls = df[required].isna().sum()
    bad = nulls[nulls > 0]
    if not bad.empty:
        errors.append(f"Nulls found: {bad.to_dict()}")

    # 4. Sales must be positive, quantity at least 1
    if (df["sales"] <= 0).any():
        errors.append("Found sales <= 0")
    if (df["quantity"] < 1).any():
        errors.append("Found quantity < 1")

    # 5. Discount between 0 and 1
    if not df["discount"].between(0, 1).all():
        errors.append("Discount outside 0-1")

    # 6. Ship date cannot be before order date
    if (df["ship_date"] < df["order_date"]).any():
        errors.append("Ship date before order date")

    # 7. No duplicate rows (row_id is unique)
    if df["row_id"].duplicated().any():
        errors.append("Duplicate row_id values")

    if errors:
        raise ValueError("Validation failed:\n- " + "\n- ".join(errors))

    print(f"Validation passed: {len(df)} rows OK")
    return df

if __name__ == "__main__":
    from etl.extract import extract
    from etl.transform import transform
    validate(transform(extract("Sample - Superstore.csv")))