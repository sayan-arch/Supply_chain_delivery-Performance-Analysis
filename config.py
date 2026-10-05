"""Project settings and file paths."""

from pathlib import Path


# Folder containing this config.py file and main.py
PROJECT_ROOT = Path(__file__).resolve().parent

# Data and output folders
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR
DATA_PROCESSED_DIR = DATA_DIR
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Input and cleaned data files
RAW_DATA_FILE = DATA_DIR / "raw.csv"
PROCESSED_DATA_FILE = DATA_DIR / "processed.csv"

# Analysis settings
MIN_GROUP_SHIPMENTS = 20
ON_TIME_TARGET_PERCENT = 90.0
RANDOM_SEED = 42

# Columns that must exist in the raw CSV
REQUIRED_COLUMNS = [
    "Shipment_ID",
    "Order_Date",
    "Ship_Date",
    "Expected_Delivery",
    "Actual_Delivery",
    "Carrier",
    "Origin_Region",
    "Destination_Region",
    "Route",
    "Shipping_Mode",
    "Distance_KM",
    "Delay_Reason",
    "Shipment_Status",
    "Shipping_Cost",
    "Priority",
]