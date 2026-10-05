"""Run the supply-chain delivery analysis."""

import json

import pandas as pd

from config import (
    DATA_DIR,
    MIN_GROUP_SHIPMENTS,
    OUTPUTS_DIR,
    REQUIRED_COLUMNS,
)
from src.analysis import (
    calculate_kpis,
    carrier_performance,
    cost_efficiency_performance,
    delay_reason_performance,
    distance_delay_correlation,
    monthly_delivery_performance,
    overall_delivery_performance,
    priority_performance,
    region_performance,
    route_performance,
    shipping_mode_performance,
    underperforming_groups,
)
from src.data_loader import inspect_data, load_data
from src.preprocessing import clean_shipments
from src.visualization import create_all_visualizations


def format_value(value, digits=2):
    """Format a number for readable output and report text."""
    if pd.isna(value):
        return "Not available"
    return f"{value:,.{digits}f}"


def save_summary_table(dataframe, output_path):
    """Save a summary, making its named index a normal CSV column."""
    if dataframe.index.name:
        dataframe = dataframe.reset_index()

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )


def write_business_report(
    kpis,
    carrier_summary,
    route_summary,
    region_summary,
    reason_summary,
    mode_summary,
    monthly_summary,
    distance_correlation,
    high_volume_carriers,
    high_volume_routes,
    audit,
):
    """Write the business findings report required by the project."""

    def format_percent(value):
        """Render a ratio or percentage without crashing on missing data."""
        if pd.isna(value):
            return "Not available"
        if 0 <= value <= 1:
            value = value * 100
        return format_value(value)

    kpi_lookup = {
        str(key).strip(): value for key, value in zip(kpis["KPI"], kpis["Value"])
    }
    on_time_rate = format_percent(
        kpi_lookup.get("On-time delivery rate (%)", pd.NA)
    )
    late_rate = format_percent(
        kpi_lookup.get("Late shipment percentage (%)", pd.NA)
    )
    avg_delay_days = format_value(
        kpi_lookup.get("Average delay among late shipments (days)", pd.NA)
    )

    if high_volume_carriers.empty:
        lowest_rate_carrier = "No carrier met the shipment threshold"
        highest_delay_carrier = "Not available"
    else:
        lowest_rate_carrier = str(high_volume_carriers.index[0])
        highest_delay_carrier = str(
            high_volume_carriers["Avg_Delay_Among_Late"].idxmax()
        )

    if high_volume_routes.empty:
        lowest_rate_route = "No route met the shipment threshold"
        routes_to_review = "No routes met the shipment threshold."
    else:
        lowest_rate_route = str(high_volume_routes.index[0])
        route_delay_rank = high_volume_routes.sort_values(
            "Avg_Delay_Among_Late",
            ascending=False,
        )
        routes_to_review = ", ".join(
            (
                f"{route} ({format_value(row['Avg_Delay_Among_Late'])} "
                f"average late days, {int(row['Shipments'])} shipments)"
            )
            for route, row in route_delay_rank.head(5).iterrows()
        )

    if region_summary.empty:
        lowest_rate_region = "Not available"
    else:
        lowest_rate_region = str(region_summary["On_Time_Rate"].idxmin())

    if reason_summary.empty:
        most_common_reason = "No reasons recorded for late shipments"
        highest_delay_reason = "Not available"
    else:
        most_common_reason = str(reason_summary.index[0])
        highest_delay_reason = str(reason_summary["Avg_Delay"].idxmax())

    if mode_summary.empty:
        lowest_rate_mode = "Not available"
        highest_rate_mode = "Not available"
    else:
        lowest_rate_mode = str(mode_summary["On_Time_Rate"].idxmin())
        highest_rate_mode = str(mode_summary["On_Time_Rate"].idxmax())

    if len(monthly_summary) >= 2:
        first_month = monthly_summary.index[0]
        last_month = monthly_summary.index[-1]
        rate_change = (
            monthly_summary["On_Time_Rate"].iloc[-1]
            - monthly_summary["On_Time_Rate"].iloc[0]
        )

        if rate_change > 0:
            trend_word = "increased"
        elif rate_change < 0:
            trend_word = "decreased"
        else:
            trend_word = "was unchanged"

        monthly_finding = (
            f"From {first_month} to {last_month}, the on-time rate "
            f"{trend_word} by {format_value(abs(rate_change))} percentage "
            "points. Check monthly shipment counts and partial-month "
            "coverage before drawing conclusions."
        )
    else:
        monthly_finding = (
            "A month-to-month trend could not be compared because fewer "
            "than two delivery months were available."
        )

    audit_summary = json.dumps(audit, indent=2, default=str)

    report = f"""# Supply Chain Delivery Performance Findings

## Executive Summary
- Overall on-time rate: {on_time_rate}%
- Late shipment rate: {late_rate}%
- Average delay among eligible deliveries: {avg_delay_days} days
- Lowest-performing high-volume carrier: {lowest_rate_carrier}
- Carrier with the worst late delay: {highest_delay_carrier}
- Lowest-performing high-volume route: {lowest_rate_route}
- Lowest on-time destination region: {lowest_rate_region}
- Most common late-delay reason: {most_common_reason}
- Highest average delay reason: {highest_delay_reason}
- Lowest on-time shipping mode: {lowest_rate_mode}
- Highest on-time shipping mode: {highest_rate_mode}

## Actionable Findings
{monthly_finding}

Routes with the largest late-delay averages are: {routes_to_review}

The relationship between distance and delay is {format_value(distance_correlation)} (higher values suggest stronger positive correlation).

## Data Quality Audit
```json
{audit_summary}
```
"""

    report_path = OUTPUTS_DIR / "business_findings.md"
    report_path.write_text(report, encoding="utf-8")


def main():
    """Execute the complete supply-chain analysis workflow."""
    data_folder = DATA_DIR
    data_folder.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_shipments = load_data()

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in raw_shipments.columns
    ]
    if missing_columns:
        raise ValueError(
            "The raw CSV is missing required columns: " + ", ".join(missing_columns)
        )

    if len(raw_shipments) < 5000:
        raise ValueError(
            f"The project requires at least 5,000 raw rows; "
            f"the CSV has {len(raw_shipments):,}."
        )

    print("Raw data inspection:")
    inspect_data(raw_shipments)

    processed, audit = clean_shipments(raw_shipments)

    processed["Route"] = (
        processed["Origin_Region"].astype("string").str.strip()
        + "-"
        + processed["Destination_Region"].astype("string").str.strip()
    )

    valid_order_sequence = (
        processed["Order_Date"].notna()
        & processed["Ship_Date"].notna()
        & processed["Order_Date"].le(processed["Ship_Date"]).fillna(False)
    )

    processed["Outcome_Eligible"] = (
        processed["Outcome_Eligible"].fillna(False) & valid_order_sequence
    )
    processed.loc[~processed["Outcome_Eligible"], "On_Time"] = pd.NA

    is_late = processed["Delay_Days"].gt(0).fillna(False)
    eligible_late = processed["Outcome_Eligible"] & is_late
    eligible_not_late = processed["Outcome_Eligible"] & ~is_late
    reason_missing = processed["Delay_Reason"].isna()

    processed.loc[reason_missing & eligible_late, "Delay_Reason"] = "Unspecified"
    processed.loc[
        reason_missing & eligible_not_late,
        "Delay_Reason",
    ] = "Not applicable"

    processed_path = data_folder / "processed.csv"
    processed.to_csv(
        processed_path,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d",
    )

    order_after_ship = (
        processed["Order_Date"].notna()
        & processed["Ship_Date"].notna()
        & processed["Order_Date"].gt(processed["Ship_Date"])
    )
    unusually_large_delay = processed["Delay_Days"].abs().gt(30).fillna(False)
    delivered_without_eligible_dates = (
        processed["Shipment_Status"].eq("Delivered") & ~processed["Outcome_Eligible"]
    )

    review_mask = (
        processed["Long_Delivery_Flag"].fillna(False)
        | processed["Long_Delay_Flag"].fillna(False)
        | unusually_large_delay
        | order_after_ship
        | delivered_without_eligible_dates
    )

    review_rows = processed.loc[review_mask].copy()
    review_rows.to_csv(
        OUTPUTS_DIR / "data_quality_review.csv",
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d",
    )

    eligible_deliveries = processed.loc[processed["Outcome_Eligible"]].copy()
    outside_expected_delay_range = eligible_deliveries.loc[
        ~eligible_deliveries["Delay_Days"].between(-2, 10),
        [
            "Shipment_ID",
            "Ship_Date",
            "Expected_Delivery",
            "Actual_Delivery",
            "Delay_Days",
        ],
    ]

    if not outside_expected_delay_range.empty:
        print("\nExamples outside the dataset's expected -2 to +10 day range:")
        print(outside_expected_delay_range.head(10).to_string(index=False))
        raise ValueError(
            "Unexpected delay values found. Check date parsing in "
            "src/preprocessing.py and inspect outputs/data_quality_review.csv."
        )

    kpis = calculate_kpis(processed)
    overall_counts, delay_distribution = overall_delivery_performance(eligible_deliveries)
    carrier_summary = carrier_performance(eligible_deliveries)
    route_summary = route_performance(eligible_deliveries)
    region_summary = region_performance(eligible_deliveries)
    reason_summary = delay_reason_performance(eligible_deliveries)
    mode_summary = shipping_mode_performance(eligible_deliveries)
    monthly_summary = monthly_delivery_performance(eligible_deliveries)
    distance_correlation = distance_delay_correlation(eligible_deliveries)

    priority_summary = priority_performance(eligible_deliveries)
    cost_efficiency = cost_efficiency_performance(processed)

    high_volume_carriers = underperforming_groups(carrier_summary, MIN_GROUP_SHIPMENTS)
    high_volume_routes = underperforming_groups(route_summary, MIN_GROUP_SHIPMENTS)

    print(f"\nRaw rows: {len(raw_shipments):,}")
    print(f"Cleaned rows: {len(processed):,}")
    print("Eligible delivered shipments: " f"{int(processed['Outcome_Eligible'].sum()):,}")
    print(f"Processed CSV saved to: {processed_path}")

    print("\nKey performance indicators:")
    print(kpis.to_string(index=False))

    print("\nOn-time versus late shipments:")
    print(overall_counts.to_string(index=False))

    print("\nDelay-day distribution:")
    print(delay_distribution.to_string(index=False))

    print("\nCarrier performance:")
    print(carrier_summary.to_string())

    print("\nRoute performance:")
    print(route_summary.to_string())

    print("\nDestination-region performance:")
    print(region_summary.to_string())

    print("\nDelay reason analysis:")
    print(reason_summary.to_string())

    print("\nShipping-mode performance:")
    print(mode_summary.to_string())

    print("\nMonthly delivery trend:")
    print(monthly_summary.to_string())

    print("\nDistance-delay correlation:")
    print(format_value(distance_correlation))

    print("\nPriority-level performance:")
    print(priority_summary.to_string())

    print("\nShipping cost per kilometer by mode:")
    print(cost_efficiency.to_string())

    print(f"\nCarriers with at least {MIN_GROUP_SHIPMENTS} shipments:")
    print(high_volume_carriers.to_string())

    print(f"\nRoutes with at least {MIN_GROUP_SHIPMENTS} shipments:")
    print(high_volume_routes.to_string())

    kpis.to_csv(OUTPUTS_DIR / "kpi_summary.csv", index=False, encoding="utf-8")

    summary_tables = {
        "overall_delivery_counts.csv": overall_counts,
        "delay_distribution.csv": delay_distribution,
        "carrier_performance.csv": carrier_summary,
        "route_performance.csv": route_summary,
        "region_performance.csv": region_summary,
        "delay_reason_analysis.csv": reason_summary,
        "shipping_mode_performance.csv": mode_summary,
        "monthly_delivery_trend.csv": monthly_summary,
        "high_volume_carriers.csv": high_volume_carriers,
        "high_volume_routes.csv": high_volume_routes,
        "priority_performance.csv": priority_summary,
        "shipping_cost_per_km.csv": cost_efficiency,
    }

    for filename, table in summary_tables.items():
        save_summary_table(table, OUTPUTS_DIR / filename)

    (OUTPUTS_DIR / "data_cleaning_audit.json").write_text(
        json.dumps(audit, indent=2, default=str),
        encoding="utf-8",
    )

    create_all_visualizations(
        eligible_deliveries,
        overall_counts,
        carrier_summary,
        route_summary,
        region_summary,
        reason_summary,
        monthly_summary,
        OUTPUTS_DIR,
    )

    write_business_report(
        kpis,
        carrier_summary,
        route_summary,
        region_summary,
        reason_summary,
        mode_summary,
        monthly_summary,
        distance_correlation,
        high_volume_carriers,
        high_volume_routes,
        audit,
    )

    print(f"\nTables, charts, audit, and report saved in: {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()

