import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def load_to_db(
    df: pd.DataFrame,
    table_name: str = "daily_stock_prices",
) -> None:
    load_dotenv()
    postgre_user = os.getenv("POSTGRES_USER")
    postgre_password = os.getenv("POSTGRES_PASSWORD")
    postgre_host = os.getenv("POSTGRES_HOST")
    postgre_port = os.getenv("POSTGRES_PORT")
    postgre_db = os.getenv("POSTGRES_DB")

    DATABASE_URL = f"postgresql+psycopg2://{postgre_user}:{postgre_password}@{postgre_host}:{postgre_port}/{postgre_db}"
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT version();"))
            print("Conectado com sucesso! Versão do banco:")
            for linha in resultado:
                print(linha[0])
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        raise

    df.to_sql("staging_stock_prices", con=engine, if_exists="replace", index=False)

    BASE_DIR = Path(__file__).resolve().parent.parent
    sql_path = BASE_DIR / "sql" / "Query.sql"
    create_load_query = sql_path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(create_load_query))
        print("Dados carregados no banco com sucesso.")


if __name__ == "__main__":
    from src.transform import transform_daily_stock

    BASE_DIR = Path(__file__).resolve().parent.parent
    json_file = BASE_DIR / "data" / "raw" / "IBM_daily.json"

    df = transform_daily_stock(json_file)
    load_to_db(df)
