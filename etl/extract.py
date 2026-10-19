import pandas as pd

def extract(path: str) -> pd.DataFrame:
    # Kaggle Superstore is often not UTF-8
    df = pd.read_csv(path, encoding="windows-1252")
    print(f"Extracted {len(df)} rows, {len(df.columns)} columns")
    return df

if __name__ == "__main__":
    df = extract("Sample - Superstore.csv")
    print(df.head())
    print(df.dtypes)
    print(df.isna().sum())