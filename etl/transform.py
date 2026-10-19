import pandas as pd
from etl.extract import extract

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Clean column names: "Order Date" -> "order_date"
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # 2. Text -> real dates (month/day/year)
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y")

    # 3. Postal code is an ID, not a number (restore leading zeros)
    df["postal_code"] = df["postal_code"].astype(str).str.zfill(5)

    # 4. Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    print(f"Removed {before - len(df)} duplicate rows")

    # 5. New columns
    df["total_cost"] = df["sales"] - df["profit"]
    df["unit_cost"] = (df["total_cost"] / df["quantity"]).round(2)
    df["profit_margin"] = (df["profit"] / df["sales"]).round(4)
    df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days

    return df

if __name__ == "__main__":
    raw = extract("Sample - Superstore.csv")
    clean = transform(raw)
    print(clean.head())
    print(clean.dtypes)