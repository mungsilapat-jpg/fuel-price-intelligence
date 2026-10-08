from pathlib import Path

import pandas as pd

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXTHUS"

df = pd.read_csv(URL)
df.columns = ["period", "usd_thb"]
df["period"] = pd.to_datetime(df["period"])
df["usd_thb"] = pd.to_numeric(df["usd_thb"], errors="coerce")  # วันหยุดเป็น "." จะกลายเป็น NaN

out = Path("data/bronze/fred_usdthb_daily.parquet")
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out, index=False)

print(f"Saved {len(df)} rows to {out}")
print(df.tail())