from pathlib import Path
from src.data_loader import load_data
from src.preprocessing import clean_shipments
import pandas as pd
from src.analysis import calculate_kpis

def main():
    raw_shipments = load_data()
    cleaned, audit = clean_shipments(raw_shipments)

    cleaned["Route"] = (
        cleaned["Origin_Region"] + "-" + cleaned["Destination_Region"]
    )

    cleaned = cleaned[
        cleaned["Shipment_Status"].eq("Delivered")
    ].copy()

    late = cleaned["Delay_Days"].gt(0)
    reason_missing = cleaned["Delay_Reason"].isna()

    cleaned.loc[reason_missing & late, "Delay_Reason"] = "Unspecified"
    cleaned.loc[reason_missing & ~late, "Delay_Reason"] = "Not applicable"

    required_fields = [
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
        "Shipping_Cost",
        "Priority",
        "Delivery_Days",
        "Delay_Days",
    ]

    complete_rows = cleaned[required_fields].notnull().all(axis=1)

    valid_rows = (
        (cleaned["Order_Date"] <= cleaned["Ship_Date"])
        & (cleaned["Ship_Date"] <= cleaned["Expected_Delivery"])
        & (cleaned["Ship_Date"] <= cleaned["Actual_Delivery"])
        & (cleaned["Distance_KM"] > 0)
        & (cleaned["Shipping_Cost"] >= 0)
        & cleaned["Delivery_Days"].between(0, 30)
        & (cleaned["Delay_Days"] <= 30)
    )

    cleaned = cleaned[complete_rows & valid_rows].copy()

    project_folder = Path(__file__).resolve().parent
    output_path = project_folder / "data" / "processed.csv"
    cleaned.to_csv(output_path, index=False)

    print(f"Raw rows: {len(raw_shipments):,}")
    print(f"Rows in processed file: {len(cleaned):,}")
    print(f"Saved to: {output_path}")

    kpis = calculate_kpis(processed=cleaned)
    print(kpis.to_string(index=False))


if __name__ == "__main__":
    main()