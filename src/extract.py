import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


def get_alpha_vantage_data(
    api_key: str | None,
    symbol: str = "IBM",
    outputsize: str = "compact",
    function: str = "TIME_SERIES_DAILY",
) -> Path:

    if not api_key:
        raise ValueError("Chave de API não informada ou ausente no .env")

    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize={outputsize}&apikey={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    resp_json = response.json()

    if (
        "Error Message" in resp_json
        or "Information" in resp_json
        or "Note" in resp_json
    ):
        msg = (
            resp_json.get("Error Message")
            or resp_json.get("Information")
            or resp_json.get("Note")
        )
        raise ValueError(f"Erro na API Alpha Vantage: {msg}")

    BASE_DIR = Path(__file__).resolve().parent.parent
    pasta_destino = BASE_DIR / "data" / "raw"
    pasta_destino.mkdir(parents=True, exist_ok=True)
    caminho_completo = pasta_destino / f"{symbol}_daily.json"

    with open(caminho_completo, "w") as f:
        json.dump(resp_json, f, indent=2)

    print(f"Dados salvos em: {caminho_completo}")
    return caminho_completo


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    get_alpha_vantage_data(api_key)
