import sys
from prefect import flow, task
from etl.extract import extract
from etl.transform import transform
from etl.validate import validate
from etl.load import load

CSV_PATH = "Sample - Superstore.csv"

@task(retries=2, retry_delay_seconds=10)
def extract_task():
    return extract(CSV_PATH)

@task
def transform_task(df):
    return transform(df)

@task
def validate_task(df):
    return validate(df)

@task(retries=2, retry_delay_seconds=10)
def load_task(df):
    return load(df)

@flow(name="superstore-etl", log_prints=True)
def run_pipeline():
    raw = extract_task()
    clean = transform_task(raw)
    checked = validate_task(clean)
    rows = load_task(checked)
    print(f"Pipeline finished: {rows} rows in warehouse")

if __name__ == "__main__":
    if "--schedule" in sys.argv:
        # runs every day at 2 AM
        run_pipeline.serve(name="superstore-daily", cron="0 2 * * *")
    else:
        run_pipeline()