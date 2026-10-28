import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

url = URL.create(
    "postgresql+pg8000",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
    port=int(os.getenv("POSTGRES_PORT", "5434")),
    database=os.getenv("POSTGRES_DB"),
)
engine = create_engine(url)

with engine.connect() as conn:
    df = pd.read_sql(
        text("select * from gold.fct_fuel_price_monthly order by item, month"), conn
    )

FEATURES = [
    "retail_price_lag1",
    "brent_baht_per_litre_lag1",
    "brent_baht_per_litre_lag2",
    "brent_baht_per_litre_lag3",
]
TARGET = "retail_price_baht"
TEST_MONTHS = 24

for col in [TARGET] + FEATURES:
    df[col] = df[col].astype(float)
df["month"] = pd.to_datetime(df["month"])
df = df.dropna(subset=FEATURES).copy()

metric_rows = []
pred_frames = []

for item, g in df.groupby("item"):
    g = g.sort_values("month").reset_index(drop=True)
    train, test = g.iloc[:-TEST_MONTHS], g.iloc[-TEST_MONTHS:]

    x_train = np.column_stack([np.ones(len(train)), train[FEATURES].to_numpy()])
    y_train = train[TARGET].to_numpy()
    beta, *_ = np.linalg.lstsq(x_train, y_train, rcond=None)

    x_test = np.column_stack([np.ones(len(test)), test[FEATURES].to_numpy()])
    y_test = test[TARGET].to_numpy()

    pred_naive = test["retail_price_lag1"].to_numpy()
    pred_linear = x_test @ beta

    for name, pred in [("naive_last_month", pred_naive), ("linear_brent_lags", pred_linear)]:
        err = y_test - pred
        metric_rows.append(
            {
                "item": item,
                "model": name,
                "mae": float(np.abs(err).mean()),
                "rmse": float(np.sqrt((err ** 2).mean())),
                "n_train": len(train),
                "n_test": len(test),
            }
        )

    pred_frames.append(
        pd.DataFrame(
            {
                "month": test["month"].dt.date,
                "item": item,
                "actual": y_test,
                "pred_naive": pred_naive,
                "pred_linear": pred_linear,
            }
        )
    )

metrics = pd.DataFrame(metric_rows)
preds = pd.concat(pred_frames, ignore_index=True)

metrics.to_sql("model_metrics", engine, schema="gold", if_exists="replace", index=False)
preds.to_sql("model_predictions", engine, schema="gold", if_exists="replace", index=False, chunksize=500)

print(metrics.round(3).to_string(index=False))
print(f"Saved {len(metrics)} metric rows and {len(preds)} prediction rows to schema gold")