import json
from pathlib import Path

import pandas as pd


def transform_daily_stock(file_path: Path | str) -> pd.DataFrame:
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado no caminho: {file_path}")

    md_symbol = data["Meta Data"]["2. Symbol"]
    df = (
        pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
        .reset_index()
        .rename(columns={"index": "date"})
    )
    df["symbol"] = md_symbol
    df["date"] = pd.to_datetime(df["date"])
    df.columns = df.columns.str.replace(r"\d+\.\s+", "", regex=True)
    df[["open", "high", "low", "close"]] = (
        df[["open", "high", "low", "close"]].astype(float).round(2)
    )
    df["volume"] = df["volume"].astype(int)
    df = df.sort_values(by="date")

    return df


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    caminho_arquivo = BASE_DIR / "data" / "raw" / "IBM_daily.json"
    transform_daily_stock(caminho_arquivo)
