import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def get_engine():
    return create_engine(os.environ["DATABASE_URL"])

if __name__ == "__main__":
    with get_engine().connect() as conn:
        print(conn.execute(text("SELECT version()")).scalar())