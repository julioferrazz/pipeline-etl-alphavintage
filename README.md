# Alpha Vantage Stock ETL

Pipeline de Engenharia de Dados (ETL) em Python que extrai cotações diárias do mercado financeiro através da API da **Alpha Vantage**, realiza a limpeza e tipagem dos dados com **Pandas** e armazena os registros em um banco **PostgreSQL** utilizando estratégia de *staging* e *upsert* idempotente.

---

## O que a API está puxando?

A extração consome o endpoint **`TIME_SERIES_DAILY`** da [Alpha Vantage](https://www.alphavantage.co/), utilizando por padrão:
- **Função (`function`):** `TIME_SERIES_DAILY` (série histórica diária)
- **Ativo (`symbol`):** `IBM` *(configurável)*
- **Tamanho (`outputsize`):** `compact` (retorna os últimos **100 pregões**)

Para cada dia negociado, o pipeline coleta e processa os seguintes campos:

| Coluna | Tipo no Banco | Descrição |
| :--- | :--- | :--- |
| `date` | `DATE` | Data do pregão (parte da chave primária) |
| `symbol` | `VARCHAR` | Código/ticker da ação (parte da chave primária) |
| `open` | `NUMERIC(10,2)` | Preço de abertura |
| `high` | `NUMERIC(10,2)` | Preço máximo atingido no dia |
| `low` | `NUMERIC(10,2)` | Preço mínimo atingido no dia |
| `close` | `NUMERIC(10,2)` | Preço de fechamento |
| `volume` | `BIGINT` | Volume total de ações negociadas |

---

## Principais Pontos da Arquitetura

- **Extração (`src/extract.py`):** Faz a requisição HTTP com validação de status e tratamento específico para mensagens de erro ou limite de requisições da Alpha Vantage (`Error Message`, `Information`, `Note`). Salva o retorno bruto em `data/raw/{symbol}_daily.json`.
- **Transformação (`src/transform.py`):** Converte o JSON para DataFrame Pandas, remove os prefixos numéricos das colunas da API (ex.: `1. open` → `open`), converte datas, arredonda valores monetários para 2 casas decimais e ordena os registros cronologicamente.
- **Carga Idempotente (`src/load.py` e `sql/Query.sql`):**
  1. Carrega o DataFrame tratado na tabela intermediária `staging_stock_prices`.
  2. Garante a criação da tabela final `daily_stock_prices` com chave primária composta `(symbol, date)`.
  3. Executa um **upsert** (`INSERT ... ON CONFLICT (symbol, date) DO UPDATE`), evitando duplicidades e atualizando valores caso o pipeline seja reexecutado.
- **Containerização (`Dockerfile` e `docker-compose.yml`):** Orquestra o banco `postgres:16-alpine` (com *healthcheck* e volume persistente) e o container da aplicação Python (`python:3.12-slim`).

---

## Estrutura do Projeto

```text
alphavantage-etl/
├── data/
│   ├── raw/                 # JSONs brutos extraídos da API
│   └── processed/           # Dados processados locais
├── sql/
│   ├── Query.sql            # DDL da tabela final e query de upsert
│   └── analytics.sql        # Consultas analíticas sobre os dados
├── src/
│   ├── extract.py           # Módulo de extração da API
│   ├── transform.py         # Módulo de limpeza e transformação
│   └── load.py              # Módulo de carga no PostgreSQL
├── .env.example             # Modelo de variáveis de ambiente
├── docker-compose.yml       # Orquestração dos serviços (Postgres + ETL)
├── Dockerfile               # Imagem da aplicação Python
├── main.py                  # Ponto de entrada do pipeline completo
└── requirements.txt         # Dependências Python
```

---

## Como Rodar via Docker

### Pré-requisitos
- [Docker](https://www.docker.com/) e **Docker Compose** instalados.
- Uma chave de API gratuita da [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

### 1. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto a partir do `.env.example`:

```bash
cp .env.example .env
```

Preencha o `.env` com sua chave da API e as credenciais do banco (mantenha `POSTGRES_HOST=postgres` para a comunicação entre os containers):

```env
ALPHA_VANTAGE_API_KEY=sua_chave_aqui
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=stocks_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

### 2. Execute a aplicação

Na raiz do projeto, execute:

```bash
docker compose up --build
```

O Docker Compose irá:
1. Subir o container do **PostgreSQL** (`postgres:16-alpine`) e aguardar o banco ficar saudável (*healthcheck*).
2. Construir a imagem do serviço **`etl`** e executar `python main.py`.
3. Salvar o JSON bruto localmente na pasta `./data` (mapeada como volume) e inserir os dados tratados no PostgreSQL.

### Comandos úteis do Docker

- **Rodar apenas o pipeline ETL novamente** (com o Postgres já de pé):
  ```bash
  docker compose up etl
  ```
- **Consultar os dados diretamente no PostgreSQL do container:**
  ```bash
  docker compose exec postgres psql -U postgres -d stocks_db -c "SELECT * FROM daily_stock_prices ORDER BY date DESC LIMIT 10;"
  ```
- **Encerrar os containers:**
  ```bash
  docker compose down
  ```
- **Encerrar os containers e apagar os dados persistidos do banco:**
  ```bash
  docker compose down -v
  ```
