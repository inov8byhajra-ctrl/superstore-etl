import pandas as pd
from sqlalchemy import text
from etl.db import get_engine

TABLE = "superstore_sales"

DDL = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    row_id          INTEGER PRIMARY KEY,
    order_id        VARCHAR(20) NOT NULL,
    order_date      DATE NOT NULL,
    ship_date       DATE NOT NULL,
    ship_mode       VARCHAR(30),
    customer_id     VARCHAR(20) NOT NULL,
    customer_name   VARCHAR(100),
    segment         VARCHAR(30),
    country         VARCHAR(50),
    city            VARCHAR(100),
    state           VARCHAR(100),
    postal_code     VARCHAR(10),
    region          VARCHAR(30),
    product_id      VARCHAR(30) NOT NULL,
    category        VARCHAR(50),
    sub_category    VARCHAR(50),
    product_name    TEXT,
    sales           NUMERIC(12,4),
    quantity        INTEGER,
    discount        NUMERIC(5,2),
    profit          NUMERIC(12,4),
    total_cost      NUMERIC(12,4),
    unit_cost       NUMERIC(12,4),
    profit_margin   NUMERIC(8,4),
    shipping_days   INTEGER
);
"""

def load(df: pd.DataFrame) -> int:
    engine = get_engine()
    # engine.begin() = one transaction: if anything fails, nothing is saved
    with engine.begin() as conn:
        conn.execute(text(DDL))
        conn.execute(text(f"TRUNCATE TABLE {TABLE}"))  # makes re-runs safe
        df.to_sql(TABLE, conn, if_exists="append", index=False,
                  method="multi", chunksize=1000)
        count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE}")).scalar()
    print(f"Loaded {count} rows into {TABLE}")
    return count

if __name__ == "__main__":
    from etl.extract import extract
    from etl.transform import transform
    from etl.validate import validate
    load(validate(transform(extract("Sample - Superstore.csv"))))