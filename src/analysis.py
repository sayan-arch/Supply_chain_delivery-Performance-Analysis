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


def overall_delivery_performance(df):
    """Count on-time and late deliveries and show the delay distribution."""

    on_time_count = int((df["On_Time"] == 1).sum())
    late_count = int((df["On_Time"] == 0).sum())

    overall_counts = pd.DataFrame({
        "Delivery_Status": ["On time", "Late"],
        "Shipments": [on_time_count, late_count],
    })

    delay_distribution = (
        df["Delay_Days"]
        .value_counts()
        .sort_index()
        .rename_axis("Delay_Days")
        .reset_index(name="Shipments")
    )

    return overall_counts, delay_distribution


def carrier_performance(df):
    """Compare delivery performance across carriers."""

    summary = df.groupby("Carrier").agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delay=("Delay_Days", "mean"),
        Avg_Delay_Among_Late=(
            "Delay_Days",
            lambda values: values[values > 0].mean(),
        ),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
        Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    )

    summary["On_Time_Rate"] = summary["On_Time_Rate"] * 100

    return summary.sort_values("On_Time_Rate")


def route_performance(df):
    """Compare delivery performance across routes."""

    summary = df.groupby("Route").agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delay=("Delay_Days", "mean"),
        Avg_Delay_Among_Late=(
            "Delay_Days",
            lambda values: values[values > 0].mean(),
        ),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
    )

    summary["On_Time_Rate"] = summary["On_Time_Rate"] * 100

    return summary.sort_values("On_Time_Rate")


def region_performance(df):
    """Compare delivery performance by destination region."""

    summary = df.groupby("Destination_Region").agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delay=("Delay_Days", "mean"),
        Avg_Delay_Among_Late=(
            "Delay_Days",
            lambda values: values[values > 0].mean(),
        ),
    )

    summary["On_Time_Rate"] = summary["On_Time_Rate"] * 100

    return summary.sort_values("On_Time_Rate")

def delay_reason_performance(df):
    """Summarize reasons recorded for late shipments."""
    late = df.loc[df["Delay_Days"] > 0]

    summary = late.groupby("Delay_Reason").agg(
        Delayed_Shipments=("Shipment_ID", "nunique"),
        Avg_Delay=("Delay_Days", "mean"),
        Median_Delay=("Delay_Days", "median"),
    )

    return summary.sort_values("Delayed_Shipments", ascending=False)


def shipping_mode_performance(df):
    """Compare delivery outcomes and costs across shipping modes."""
    summary = df.groupby("Shipping_Mode").agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
        Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    )

    summary["On_Time_Rate"] *= 100
    return summary.sort_values("On_Time_Rate")


def monthly_delivery_performance(df):
    """Summarize shipments by the month they were delivered."""
    monthly_df = df.copy()
    monthly_df["Month"] = (
        monthly_df["Actual_Delivery"].dt.to_period("M").astype("string")
    )

    summary = monthly_df.groupby("Month").agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delay=("Delay_Days", "mean"),
    )

    summary["On_Time_Rate"] *= 100
    return summary.sort_index()


def distance_delay_correlation(df):
    """Measure the association between distance and delay."""
    valid = df.dropna(subset=["Distance_KM", "Delay_Days"])
    return valid["Distance_KM"].corr(valid["Delay_Days"])


def underperforming_groups(summary, minimum_shipments=20):
    """Rank groups with enough shipments to compare."""
    delay_column = (
        "Avg_Delay_Among_Late"
        if "Avg_Delay_Among_Late" in summary.columns
        else "Avg_Delay"
    )

    return (
        summary.loc[summary["Shipments"] >= minimum_shipments]
        .sort_values(
            ["On_Time_Rate", delay_column],
            ascending=[True, False],
        )
    )

def _group_summary(dataframe: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Summarize delivery outcomes for each value in a grouping column."""
    summary = dataframe.groupby(group_column).agg(
        Shipments=("Shipment_ID", "nunique"),
        On_Time_Rate=("On_Time", "mean"),
        Avg_Delay=("Delay_Days", "mean"),
        Avg_Delay_Among_Late=(
            "Delay_Days",
            lambda values: values[values > 0].mean(),
        ),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
    )
    summary["On_Time_Rate"] *= 100
    return summary.sort_values("On_Time_Rate")


def priority_performance(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Compare delivery performance across shipment priority levels."""
    return _group_summary(dataframe, "Priority")


def cost_efficiency_performance(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Compare shipping cost per kilometer by shipping mode."""

    valid = dataframe.loc[
        dataframe["Distance_KM"].gt(0)
        & dataframe["Shipping_Cost"].ge(0)
    ].copy()

    valid["Cost_Per_KM"] = (
        valid["Shipping_Cost"] / valid["Distance_KM"]
    )

    return (
        valid.groupby("Shipping_Mode", observed=True)
        .agg(
            Shipments=("Shipment_ID", "count"),
            Average_Shipping_Cost=("Shipping_Cost", "mean"),
            Average_Distance_KM=("Distance_KM", "mean"),
            Average_Cost_Per_KM=("Cost_Per_KM", "mean"),
        )
        .sort_values("Average_Cost_Per_KM")
    )