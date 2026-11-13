import requests
import os
from pathlib import Path
from dotenv import load_dotenv 
import json

load_dotenv()
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

def get_alpha_vantage_data(api_key, symbol='IBM', outputsize='compact', function='TIME_SERIES_DAILY'):
    url = f'https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize={outputsize}&apikey={api_key}'
    response = requests.get(url)
    resp_json = response.json()

    response.raise_for_status()
    if "Error Message" in resp_json or "Information" in resp_json:
        msg = resp_json.get("Error Message") or resp_json.get("Information")
        raise ValueError(f"Erro na API Alpha Vantage: {resp_json['msg']}")
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    pasta_destino = BASE_DIR / "data" / "raw"
    nome_arquivo = f"{symbol}_daily.json"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)

    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    with open(caminho_completo, 'w') as f:
            json.dump(resp_json, f, indent=2)

    print(f"Dados salvos em: {caminho_completo}")
    return caminho_completo
        
if __name__ == "__main__":
    get_alpha_vantage_data(api_key)