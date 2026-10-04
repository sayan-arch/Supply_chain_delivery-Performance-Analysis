#data visualization functions

from pathlib import Path
import pandas as pd
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_FOLDER / "data" / "shipment_delivery.csv"


def load_data():
    """Load the raw shipment CSV into a Pandas DataFrame."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    return pd.read_csv(CSV_PATH)


def inspect_data(df):
    """Print a basic inspection of the raw data."""
    print("\nFirst five rows:")
    print(df.head())

    print("\nNumber of rows and columns:")
    print(df.shape)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types and non-missing values:")
    df.info()

    print("\nMissing values in each column:")
    print(df.isnull().sum())

    print("\nCompletely duplicated rows:")
    print(df.duplicated().sum())

    if "Shipment_ID" in df.columns:
        print("\nRepeated Shipment_ID values:")
        print(df["Shipment_ID"].duplicated().sum())


if __name__ == "__main__":
    shipments = load_data()
    inspect_data(shipments)