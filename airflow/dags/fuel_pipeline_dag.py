"""Thailand Fuel Price Intelligence: the full pipeline as an Airflow DAG.

fetch (3 sources) -> load Bronze -> dbt run -> dbt test -> train models

Each task calls the same scripts that run_pipeline.py uses, so the logic lives
in one place and Airflow only handles ordering, retries and scheduling.
"""
from datetime import datetime, timedelta

from airflow import DAG

try:  # Airflow 3 moved BashOperator to the standard provider
    from airflow.providers.standard.operators.bash import BashOperator
except ImportError:  # Airflow 2
    from airflow.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"
PY = "/opt/airflow/venv/bin/python"
DBT = "/opt/airflow/venv/bin/dbt"
# Keep dbt build artifacts out of the mounted project folder.
DBT_ENV = "export DBT_TARGET_PATH=/tmp/dbt_target DBT_LOG_PATH=/tmp/dbt_logs"

default_args = {
    "owner": "mung",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="fuel_price_pipeline",
    description="EIA + FRED + EPPO -> PostgreSQL bronze/silver/gold -> forecast models",
    start_date=datetime(2026, 1, 1),
    schedule="@monthly",
    catchup=False,
    default_args=default_args,
    tags=["fuel", "elt", "dbt"],
) as dag:
    fetch_brent = BashOperator(
        task_id="fetch_brent",
        bash_command=f"cd {PROJECT} && {PY} ingestion/fetch_brent.py",
    )
    fetch_usdthb = BashOperator(
        task_id="fetch_usdthb",
        bash_command=f"cd {PROJECT} && {PY} ingestion/fetch_usdthb.py",
    )
    fetch_thai_fuel = BashOperator(
        task_id="fetch_thai_fuel",
        bash_command=f"cd {PROJECT} && {PY} ingestion/fetch_thai_fuel.py",
    )
    load_bronze = BashOperator(
        task_id="load_bronze",
        bash_command=f"cd {PROJECT} && {PY} ingestion/load_to_postgres.py",
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{DBT_ENV} && cd {PROJECT}/dbt_project && {DBT} run --profiles-dir .",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT_ENV} && cd {PROJECT}/dbt_project && {DBT} test --profiles-dir .",
    )
    train_models = BashOperator(
        task_id="train_models",
        bash_command=f"cd {PROJECT} && {PY} ml/train_models.py",
    )

    [fetch_brent, fetch_usdthb, fetch_thai_fuel] >> load_bronze >> dbt_run >> dbt_test >> train_models
