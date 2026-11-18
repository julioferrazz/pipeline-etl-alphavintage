import os

from dotenv import load_dotenv

from src.extract import get_alpha_vantage_data
from src.load import load_to_db
from src.transform import transform_daily_stock


def main() -> None:
    load_dotenv()
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    print("Initiating extraction... ")
    json_file = get_alpha_vantage_data(api_key)
    print("\nExtraction done!")
    print("Transforming data...")
    df = transform_daily_stock(json_file)
    print("\nTransformation done!")
    print("Saving data in PostgreSQL...")
    load_to_db(df)
    print("\nData saved sucessfully!")


if __name__ == "__main__":
    main()
