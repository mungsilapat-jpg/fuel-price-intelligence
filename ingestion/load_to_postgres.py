import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host="127.0.0.1",
    port=int(os.getenv("POSTGRES_PORT", "5434")),
    database=os.getenv("POSTGRES_DB"),
)
engine = create_engine(url)

TABLES = {
    "eia_brent_daily": "data/bronze/eia_brent_daily.parquet",
    "fred_usdthb_daily": "data/bronze/fred_usdthb_daily.parquet",
     "eppo_fuel_prices": "data/bronze/eppo_fuel_prices.parquet",
}

with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))

for table, path in TABLES.items():
    df = pd.read_parquet(path)
    df["loaded_at"] = pd.Timestamp.now(tz="UTC")
    df.to_sql(table, engine, schema="bronze", if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into bronze.{table}")