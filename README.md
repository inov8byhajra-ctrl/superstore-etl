# Superstore ETL Pipeline

An end-to-end **ETL (Extract → Transform → Validate → Load)** pipeline that takes the raw Sample Superstore CSV, cleans it, checks its quality, and loads it into a PostgreSQL warehouse table. The steps are orchestrated with **Prefect**, with retries and an optional daily schedule.

## Why this project?

Raw CSV files are not reliable enough for dashboards or analysis: dates are plain text, IDs lose leading zeros, and bad rows slip through. This pipeline automates the cleaning and guards the warehouse with data quality checks, so only trusted data lands in the database.

## Pipeline Flow

```mermaid
flowchart LR
    A[("Sample - Superstore.csv")] --> B["extract.py<br/>Read CSV (windows-1252)"]
    B --> C["transform.py<br/>Clean + enrich"]
    C --> D{"validate.py<br/>Quality checks"}
    D -- "Pass" --> E["load.py<br/>TRUNCATE + INSERT<br/>(single transaction)"]
    D -- "Fail" --> F["Pipeline stops<br/>ValueError with reasons"]
    E --> G[("PostgreSQL<br/>superstore_sales")]
    G --> H["SQL / BI tools<br/>(DBeaver, pgAdmin, dashboards)"]

    P["pipeline.py<br/>Prefect flow<br/>retries + cron schedule"] -.orchestrates.-> B
    P -.-> C
    P -.-> D
    P -.-> E
```

## Stages

| Stage | File | What it does |
|---|---|---|
| Extract | `etl/extract.py` | Reads the CSV with `windows-1252` encoding |
| Transform | `etl/transform.py` | Normalizes column names, parses dates, restores postal code leading zeros, removes duplicates, adds `total_cost`, `unit_cost`, `profit_margin`, `shipping_days` |
| Validate | `etl/validate.py` | Checks for empty data, missing columns, nulls in key columns, sales > 0, quantity >= 1, discount in 0-1, ship date >= order date, unique `row_id` |
| Load | `etl/load.py` | Creates the table if missing, truncates it, and bulk-inserts inside one transaction (all-or-nothing, safe to re-run) |
| Connect | `etl/db.py` | SQLAlchemy engine built from `DATABASE_URL` |
| Orchestrate | `pipeline.py` | Prefect flow with task retries and optional cron schedule |

## Tech Stack

- Python 3.10+
- pandas
- SQLAlchemy + psycopg2
- PostgreSQL
- Prefect
- python-dotenv

## Project Structure

```
superstore-etl/
├── .env                      # not committed (DATABASE_URL)
├── .gitignore
├── README.md
├── requirements.txt
├── Sample - Superstore.csv
├── pipeline.py
└── etl/
    ├── __init__.py
    ├── db.py
    ├── extract.py
    ├── transform.py
    ├── validate.py
    └── load.py
```

## Setup

1. **Clone and install**

   ```bash
   git clone https://github.com/<your-username>/superstore-etl.git
   cd superstore-etl
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create a PostgreSQL database** (local, Neon, or Supabase) and add a `.env` file in the project root:

   ```
   DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/dbname
   ```

3. **Place the dataset** `Sample - Superstore.csv` in the project root.

## Usage

Run every command from the project root.

```bash
# Test the database connection
python -m etl.db

# Run each stage individually (for debugging)
python -m etl.extract
python -m etl.transform
python -m etl.validate
python -m etl.load

# Run the full pipeline once
python pipeline.py

# Run it on a schedule (daily at 2 AM, keep the terminal open)
python pipeline.py --schedule
```

Optional Prefect dashboard:

```bash
prefect server start
# open http://localhost:4200
```

## Example Output

```
Extracted 9994 rows, 21 columns
Removed 0 duplicate rows
Validation passed: 9994 rows OK
Loaded 9994 rows into superstore_sales
Pipeline finished: 9994 rows in warehouse
```

## Sample Queries

```sql
SELECT * FROM superstore_sales LIMIT 10;

SELECT region,
       ROUND(SUM(sales), 2)  AS total_sales,
       ROUND(SUM(profit), 2) AS total_profit
FROM superstore_sales
GROUP BY region
ORDER BY total_profit DESC;
```

## Key Design Decisions

- **Idempotent load:** `TRUNCATE` plus insert in one transaction means re-runs never create duplicates.
- **Fail fast validation:** bad data stops the pipeline before it reaches the warehouse.
- **Retries:** extract and load tasks retry twice, 10 seconds apart, to survive transient failures.
- **Modular stages:** each step runs on its own, which makes debugging easy.

## Troubleshooting

| Error | Fix |
|---|---|
| `ModuleNotFoundError: etl` | Run from the project root using `python -m etl.<module>`, and make sure `etl/__init__.py` exists |
| `KeyError: DATABASE_URL` | Create the `.env` file in the project root |
| CSV not found | File must be named `Sample - Superstore.csv` and sit in the project root |

## Future Improvements

- Incremental loads instead of full refresh
- Unit tests with pytest
- Dockerize the pipeline and database
- Dashboard on top of the warehouse (Metabase / Power BI)

## Author

**Hajra**