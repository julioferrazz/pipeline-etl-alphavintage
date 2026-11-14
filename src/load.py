from pathlib import Path

import duckdb
import pandas as pd


def load_to_db(
    df: pd.DataFrame,
    db_path: Path | None = None,
    table_name: str = "daily_stock_prices",
) -> None:

    BASE_DIR = Path(__file__).resolve().parent.parent
    if db_path is None:
        db_path = BASE_DIR / "data" / "processed" / "stocks.duckdb"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql_path = BASE_DIR / "sql" / "Query.sql"
    with duckdb.connect(database=str(db_path)) as conn:
        create_table_query = sql_path.read_text(encoding="utf-8")
        conn.execute(create_table_query)
        conn.execute(f"INSERT OR REPLACE INTO {table_name} SELECT * FROM df")
    print(f"Loaded {len(df)} rows to {table_name} in {db_path}")


if __name__ == "__main__":
    from src.transform import transform_daily_stock

    BASE_DIR = Path(__file__).resolve().parent.parent
    json_file = BASE_DIR / "data" / "raw" / "IBM_daily.json"

    df = transform_daily_stock(json_file)
    load_to_db(df)
