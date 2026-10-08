import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EIA_API_KEY")
URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"

params = {
    "api_key": API_KEY,
    "frequency": "daily",
    "data[0]": "value",
    "facets[series][]": "RBRTE",  # Brent spot price
    "sort[0][column]": "period",
    "sort[0][direction]": "desc",
    "length": 5000,
}

resp = requests.get(URL, params=params, timeout=30)
resp.raise_for_status()

rows = resp.json()["response"]["data"]
df = pd.DataFrame(rows)
df["period"] = pd.to_datetime(df["period"])
df["value"] = pd.to_numeric(df["value"])

out = Path("data/bronze/eia_brent_daily.parquet")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out, index=False)

print(f"Saved {len(df)} rows to {out}")
print(df.head())