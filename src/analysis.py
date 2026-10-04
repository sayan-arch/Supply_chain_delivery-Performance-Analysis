import pandas as pd

def calculate_kpis(processed):
    """Calculate KPIs using the final processed dataframe."""

    total_shipments = processed["Shipment_ID"].nunique()

    delivered_mask = (
        processed["Shipment_Status"]
        .eq("Delivered")
        .fillna(False)
    )
    delivered = processed.loc[delivered_mask]

    eligible_mask = processed["Outcome_Eligible"].fillna(False)
    eligible = processed.loc[eligible_mask]

    late = eligible.loc[eligible["Delay_Days"] > 0]
    on_time_count = int(eligible["On_Time"].sum())

    if len(eligible) > 0:
        on_time_rate = on_time_count / len(eligible) * 100
        late_percentage = len(late) / len(eligible) * 100
    else:
        on_time_rate = 0
        late_percentage = 0

    results = {
        "Total shipments": total_shipments,
        "Delivered shipments": len(delivered),
        "On-time shipments": on_time_count,
        "On-time delivery rate (%)": on_time_rate,
        "Average delivery time (days)": eligible["Delivery_Days"].mean(),
        "Median delivery time (days)": eligible["Delivery_Days"].median(),
        "Average delay among late shipments (days)": late["Delay_Days"].mean(),
        "Maximum delay (days)": late["Delay_Days"].max(),
        "Late shipment count": len(late),
        "Late shipment percentage (%)": late_percentage,
        "Average shipping cost": processed["Shipping_Cost"].mean(),
        "Average distance per shipment (km)": processed["Distance_KM"].mean(),
    }

    return pd.DataFrame(
        results.items(),
        columns=["KPI", "Value"],
    )