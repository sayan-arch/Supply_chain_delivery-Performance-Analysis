from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Save charts to files without opening windows.
import matplotlib.pyplot as plt
import seaborn as sns

def plot_distance_vs_delay(df, output_folder):
    """Save a scatter plot comparing distance and delivery delay."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    sns.scatterplot(
        data=df,
        x="Distance_KM",
        y="Delay_Days",
        hue="Shipping_Mode",
        alpha=0.6,
        ax=ax,
    )

    ax.set_title("Distance vs. Delivery Delay")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Delay (days)")
    ax.legend(title="Shipping mode")

    chart_path = output_folder / "distance_vs_delay.png"
    fig.tight_layout()
    fig.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return chart_path

def save_chart(fig, path):
    """Format and save one chart."""
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def make_bar_chart(summary, column, title, x_label, output_path,
                   percentage=False):
    """Create a horizontal bar chart from a grouped summary table."""
    plot_data = summary.sort_values(column)

    fig, ax = plt.subplots(
        figsize=(9, max(4, len(plot_data) * 0.35))
    )

    ax.barh(
        plot_data.index.astype(str),
        plot_data[column],
        color="#3977a8",
    )

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("")

    if percentage:
        ax.set_xlim(0, 100)

    save_chart(fig, output_path)


def create_all_visualizations(
    df,
    overall_counts,
    carrier_summary,
    route_summary,
    region_summary,
    delay_reason_summary,
    monthly_summary,
    output_folder,
):
    """Create and save the required delivery analysis charts."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid")

    # 1. Overall on-time versus late shipments
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ["#218c74" if name == "On time" else "#d35454"
              for name in overall_counts["Delivery_Status"]]

    bars = ax.bar(
        overall_counts["Delivery_Status"],
        overall_counts["Shipments"],
        color=colors,
    )
    ax.bar_label(bars)
    ax.set_title("On-time vs. late shipments")
    ax.set_ylabel("Shipments")
    save_chart(fig, output_folder / "01_overall_on_time_vs_late.png")

    # 2. On-time rate by carrier
    make_bar_chart(
        carrier_summary,
        "On_Time_Rate",
        "On-time delivery rate by carrier",
        "On-time rate (%)",
        output_folder / "02_on_time_rate_by_carrier.png",
        percentage=True,
    )

    # 3. Average signed delay by carrier
    make_bar_chart(
        carrier_summary,
        "Avg_Delay",
        "Average delay by carrier",
        "Average delay (days)",
        output_folder / "03_average_delay_by_carrier.png",
    )

    # 4. On-time rate by route
    make_bar_chart(
        route_summary,
        "On_Time_Rate",
        "On-time delivery rate by route",
        "On-time rate (%)",
        output_folder / "04_on_time_rate_by_route.png",
        percentage=True,
    )

    # 5. Average signed delay by route
    make_bar_chart(
        route_summary,
        "Avg_Delay",
        "Average delay by route",
        "Average delay (days)",
        output_folder / "05_average_delay_by_route.png",
    )

    # 6. Number of late shipments by delay reason
    if not delay_reason_summary.empty:
        make_bar_chart(
            delay_reason_summary,
            "Delayed_Shipments",
            "Late shipments by delay reason",
            "Delayed shipments",
            output_folder / "06_delayed_shipments_by_reason.png",
        )

    # 7. On-time rate by destination region
    make_bar_chart(
        region_summary,
        "On_Time_Rate",
        "On-time delivery rate by destination region",
        "On-time rate (%)",
        output_folder / "07_on_time_rate_by_region.png",
        percentage=True,
    )

    # 8. Delay distribution by carrier
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(
        data=df,
        x="Carrier",
        y="Delay_Days",
        showfliers=False,
        ax=ax,
    )
    ax.tick_params(axis="x", rotation=20)
    ax.set_title("Delay distribution by carrier")
    ax.set_xlabel("Carrier")
    ax.set_ylabel("Delay (days)")
    save_chart(fig, output_folder / "08_delay_by_carrier_boxplot.png")

    # 9. Delivery time by shipping mode
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df,
        x="Shipping_Mode",
        y="Delivery_Days",
        showfliers=False,
        ax=ax,
    )
    ax.set_title("Delivery time by shipping mode")
    ax.set_xlabel("Shipping mode")
    ax.set_ylabel("Delivery time (days)")
    save_chart(fig, output_folder / "09_delivery_time_by_mode_boxplot.png")

    # 10. Distribution of delay days
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(
        data=df,
        x="Delay_Days",
        bins=13,
        discrete=True,
        ax=ax,
    )
    ax.set_title("Distribution of delivery delay")
    ax.set_xlabel("Delay (days; negative means early)")
    ax.set_ylabel("Shipments")
    save_chart(fig, output_folder / "10_delay_distribution_histogram.png")

    # 11. Distance versus delay, colored by shipping mode
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=df,
        x="Distance_KM",
        y="Delay_Days",
        hue="Shipping_Mode",
        alpha=0.6,
        ax=ax,
    )
    ax.set_title("Distance vs. delivery delay")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Delay (days)")
    save_chart(fig, output_folder / "11_distance_vs_delay.png")

    # 12. Monthly on-time rate, when multiple months are available
    if len(monthly_summary) > 1:
        monthly_data = monthly_summary.reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(
            data=monthly_data,
            x="Month",
            y="On_Time_Rate",
            marker="o",
            ax=ax,
        )
        ax.set_title("Monthly on-time delivery rate")
        ax.set_xlabel("Month")
        ax.set_ylabel("On-time rate (%)")
        ax.set_ylim(0, 100)
        ax.tick_params(axis="x", rotation=35)
        save_chart(fig, output_folder / "12_monthly_on_time_rate.png")

create_all_visualizations