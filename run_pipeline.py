"""Run the whole fuel price pipeline with one command.

Steps: start PostgreSQL, ingest raw data, load Bronze, run dbt (Silver, Gold),
run dbt tests, train the forecasting models. Stops at the first failed step.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

PY = sys.executable

INGEST_STEPS = [
    ("Ingest Brent prices (EIA)", [PY, "ingestion/fetch_brent.py"]),
    ("Ingest USD/THB (FRED)", [PY, "ingestion/fetch_usdthb.py"]),
    ("Ingest Thai fuel prices (EPPO)", [PY, "ingestion/fetch_thai_fuel.py"]),
]
LOAD_STEP = ("Load Bronze tables into PostgreSQL", [PY, "ingestion/load_to_postgres.py"])
DBT_STEPS = [
    (
        "dbt run (Silver and Gold)",
        ["docker", "compose", "run", "--rm", "-T", "dbt", "run", "--profiles-dir", "."],
    ),
    (
        "dbt test (data quality)",
        ["docker", "compose", "run", "--rm", "-T", "dbt", "test", "--profiles-dir", "."],
    ),
]
ML_STEP = ("Train and evaluate forecasting models", [PY, "ml/train_models.py"])


def banner(text):
    print()
    print("=" * 70)
    print(text)
    print("=" * 70, flush=True)


def run_step(name, cmd, results):
    banner(f"STEP: {name}")
    start = time.time()
    completed = subprocess.run(cmd, cwd=ROOT)
    elapsed = time.time() - start
    if completed.returncode != 0:
        results.append((name, "FAILED", elapsed))
        print_summary(results)
        print(f"\nPipeline stopped: step failed with exit code {completed.returncode}.")
        sys.exit(completed.returncode)
    results.append((name, "OK", elapsed))


def wait_for_postgres(timeout=60):
    user = os.getenv("POSTGRES_USER", "fuel")
    db = os.getenv("POSTGRES_DB", "fuel_db")
    start = time.time()
    while time.time() - start < timeout:
        check = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "pg_isready", "-U", user, "-d", db],
            cwd=ROOT,
            capture_output=True,
        )
        if check.returncode == 0:
            return True
        time.sleep(2)
    return False


def print_summary(results):
    banner("SUMMARY")
    for name, status, elapsed in results:
        print(f"{status:<7} {elapsed:6.1f}s  {name}")


def main():
    parser = argparse.ArgumentParser(description="Run the fuel price pipeline.")
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="skip downloading new data and reuse existing Parquet files",
    )
    parser.add_argument(
        "--skip-ml",
        action="store_true",
        help="skip model training",
    )
    args = parser.parse_args()

    if not (ROOT / ".env").exists():
        print("Missing .env file. Copy .env.example to .env and fill in the values.")
        sys.exit(1)

    total_start = time.time()
    results = []

    run_step("Start PostgreSQL (docker compose up)", ["docker", "compose", "up", "-d", "postgres"], results)

    banner("STEP: Wait until PostgreSQL accepts connections")
    if not wait_for_postgres():
        results.append(("Wait for PostgreSQL", "FAILED", 0.0))
        print_summary(results)
        print("\nPostgreSQL did not become ready within 60 seconds.")
        sys.exit(1)
    print("PostgreSQL is ready.")

    steps = []
    if not args.skip_fetch:
        steps.extend(INGEST_STEPS)
    steps.append(LOAD_STEP)
    steps.extend(DBT_STEPS)
    if not args.skip_ml:
        steps.append(ML_STEP)

    for name, cmd in steps:
        run_step(name, cmd, results)

    print_summary(results)
    print(f"\nPipeline finished successfully in {time.time() - total_start:.1f}s.")


if __name__ == "__main__":
    main()