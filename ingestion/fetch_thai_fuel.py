from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = (
    "https://catalog.eppo.go.th/dataset/b15f2fe3-14f0-4de5-b90e-2a5b63b4e717"
    "/resource/7d56918d-adbf-42b7-bd36-e4b33d425027/download/dataset_11_86.csv"
)

resp = requests.get(URL, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
resp.raise_for_status()

df = pd.read_csv(StringIO(resp.content.decode("utf-8-sig")))
df.columns = ["year", "month", "day", "item", "country", "price_baht", "unit"]

df["obs_date"] = pd.to_datetime(
    df["year"].astype(str) + "-" + df["month"] + "-" + df["day"].astype(str),
    format="%Y-%B-%d",
)
df["price_baht"] = pd.to_numeric(df["price_baht"], errors="coerce")

out = Path(__file__).resolve().parents[1] / "data" / "bronze" / "eppo_fuel_prices.parquet"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out, index=False)

print(f"Saved {len(df)} rows to {out}")
print(df[df["country"] == "TH-THAILAND"].tail(6))