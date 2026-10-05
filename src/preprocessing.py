import pandas as pd

#data cleaning and preprocessing functions
DATE_COLUMNS = [
    "Order_Date",
    "Ship_Date",
    "Expected_Delivery",
    "Actual_Delivery",
]

def clean_categories(df):
    """Trim extra spaces and standardize category labels."""
    category_columns = [
        "Carrier",
        "Origin_Region",
        "Destination_Region",
        "Route",
        "Shipping_Mode",
        "Delay_Reason",
        "Shipment_Status",
        "Priority",
    ]
    for column in category_columns:
        if column in df.columns:
            values = df[column].astype("string").str.strip()
            values = values.str.replace(r"\s+", " ", regex=True)
            values = values.replace("", pd.NA)
            df[column] = values.str.title()
    return df

def convert_dates(df):
    """Convert the project's mixed date formats and count invalid values."""
    invalid_date_counts = {}

    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d-%b-%Y",
    ]

    for column in DATE_COLUMNS:
        raw_dates = df[column].astype("string").str.strip()

        had_a_value = (
            raw_dates.notna()
            & raw_dates.ne("")
        )

        # Try each known format explicitly.
        converted = pd.Series(
            pd.NaT,
            index=df.index,
            dtype="datetime64[ns]",
        )

        for date_format in date_formats:
            still_unparsed = had_a_value & converted.isna()

            converted.loc[still_unparsed] = pd.to_datetime(
                raw_dates.loc[still_unparsed],
                format=date_format,
                errors="coerce",
            )

        # Fallback for spreadsheet-exported dates that include a time.
        still_unparsed = had_a_value & converted.isna()

        converted.loc[still_unparsed] = pd.to_datetime(
            raw_dates.loc[still_unparsed],
            format="mixed",
            errors="coerce",
        )

        invalid_date_counts[f"Invalid_{column}_Formats"] = int(
            (had_a_value & converted.isna()).sum()
        )

        df[column] = converted

    return df, invalid_date_counts

def convert_number(values):
    """Convert values such as '1,250 km' or '$1,250.50' to numbers."""
    cleaned = values.astype("string").str.strip()
    cleaned = cleaned.str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace(r"(?i)(km|usd|inr|rs\.?|[$₹])","",regex=True,)
    cleaned = cleaned.str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")

def clean_shipments(raw_df):
    """Clean shipment data and return it with a data-quality audit."""
    df = raw_df.copy()

    df["Shipment_ID"] = df["Shipment_ID"].astype("string").str.strip()
    df["Shipment_ID"] = df["Shipment_ID"].replace("", pd.NA)

    missing_id_count = int(df["Shipment_ID"].isna().sum())
    df = df.dropna(subset=["Shipment_ID"]).copy()

    duplicate_id_count = int(
        df.duplicated(subset="Shipment_ID").sum()
    )
    df = df.drop_duplicates(
        subset="Shipment_ID",
        keep="first",
    ).copy()

    df = clean_categories(df)
    df, invalid_date_counts = convert_dates(df)

    df["Distance_KM"] = convert_number(df["Distance_KM"])
    df["Shipping_Cost"] = convert_number(df["Shipping_Cost"])

    df["Shipment_Status"] = (
        df["Shipment_Status"]
        .astype("string")
        .str.strip()
        .str.lower()
        .replace({
            "canceled": "cancelled",
            "in-transit": "in transit",
        })
        .str.title()
    )

    actual_before_ship = (
        df["Actual_Delivery"].notnull()
        & df["Ship_Date"].notnull()
        & (df["Actual_Delivery"] < df["Ship_Date"])
    )

    expected_before_ship = (
        df["Expected_Delivery"].notnull()
        & df["Ship_Date"].notnull()
        & (df["Expected_Delivery"] < df["Ship_Date"])
    )

    actual_before_ship_count = int(actual_before_ship.sum())
    expected_before_ship_count = int(expected_before_ship.sum())

    df.loc[actual_before_ship, "Actual_Delivery"] = pd.NaT
    df.loc[expected_before_ship, "Expected_Delivery"] = pd.NaT

    missing_counts = {
        f"Missing_{column}": int(df[column].isnull().sum())
        for column in [
            "Carrier",
            "Route",
            "Order_Date",
            "Ship_Date",
            "Expected_Delivery",
            "Actual_Delivery",
        ]
    }
    #delivery matrices
    df["Delivery_Days"] = (df["Actual_Delivery"] - df["Ship_Date"]).dt.days

    df["Delay_Days"] = (df["Actual_Delivery"] - df["Expected_Delivery"]).dt.days

    required_delivery_dates = [
        "Ship_Date",
        "Expected_Delivery",
        "Actual_Delivery",
    ]

    is_delivered = (
        df["Shipment_Status"]
        .eq("Delivered")
        .fillna(False)
    )

    has_delivery_dates = df[required_delivery_dates].notnull().all(axis=1)

    df["Outcome_Eligible"] = is_delivered & has_delivery_dates
    # On-Time Delivery Flag
    # 1 means on time or early; 0 means late.
    # Ineligible shipments keep a missing value.
    df["On_Time"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="Int64",
    )

    eligible = df["Outcome_Eligible"]

    df.loc[eligible, "On_Time"] = (
        df.loc[eligible, "Actual_Delivery"]
        <= df.loc[eligible, "Expected_Delivery"]
    ).astype("int64")

    df["Long_Delivery_Flag"] = df["Delivery_Days"].gt(30).fillna(False)
    df["Long_Delay_Flag"] = df["Delay_Days"].gt(30).fillna(False)

    audit = {
        "Rows_Without_Shipment_ID_Removed": missing_id_count,
        "Duplicate_Shipment_IDs_Removed": duplicate_id_count,
        **invalid_date_counts,
        **missing_counts,
        "Actual_Delivery_Before_Ship_Date": actual_before_ship_count,
        "Expected_Delivery_Before_Ship_Date": expected_before_ship_count,
        "Delivery_Durations_Over_30_Days": int(
            df["Long_Delivery_Flag"].sum()
        ),
        "Delays_Over_30_Days": int(
            df["Long_Delay_Flag"].sum()
        ),
        "Cancelled_Shipments_Kept": int(
            df["Shipment_Status"].eq("Cancelled").sum()
        ),
        "Undelivered_Shipments_Kept": int(
            df["Shipment_Status"].eq("Undelivered").sum()
        ),
        "Delivered_Shipments_Eligible_For_KPIs": int(
            df["Outcome_Eligible"].sum()
        ),
    }

    return df, audit