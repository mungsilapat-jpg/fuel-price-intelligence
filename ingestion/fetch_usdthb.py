import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXTHUS"

# Retry a few times: a one-off DNS or network hiccup should not fail the pipeline.
for attempt in range(1, 4):
    try:
        resp = requests.get(URL, timeout=60)
        resp.raise_for_status()
        break
    except requests.RequestException as exc:
        print(f"Attempt {attempt}/3 failed: {exc}")
        if attempt == 3:
            raise
        time.sleep(10)

df = pd.read_csv(StringIO(resp.text))
df.columns = ["period", "usd_thb"]
df["period"] = pd.to_datetime(df["period"])
df["usd_thb"] = pd.to_numeric(df["usd_thb"], errors="coerce")  # วันหยุดเป็น "." จะกลายเป็น NaN

out = Path(__file__).resolve().parents[1] / "data" / "bronze" / "fred_usdthb_daily.parquet"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out, index=False)

print(f"Saved {len(df)} rows to {out}")
print(df.tail())