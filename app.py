"""Supply Chain Delivery Performance Dashboard.

Interactive Streamlit Application for tracking logistics KPIs, carrier performance,
route efficiency, and delay root-cause analysis.
"""

from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Supply Chain Delivery Performance",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern card designs, clean fonts, and KPI badges
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        transition: all 0.2s ease-in-out;
    }
    /* Header title highlight */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6 0%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"


# ---------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------
@st.cache_data
def load_processed_data() -> pd.DataFrame:
    """Load cleaned dataset from disk or trigger fallback cleaning."""
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
    else:
        # Fallback if processed.csv does not exist yet
        from src.data_loader import load_data
        from src.preprocessing import clean_shipments

        raw = load_data()
        df, _ = clean_shipments(raw)
        df.to_csv(DATA_PATH, index=False)

    date_cols = ["Order_Date", "Ship_Date", "Expected_Delivery", "Actual_Delivery"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "Route" not in df.columns and "Origin_Region" in df.columns and "Destination_Region" in df.columns:
        df["Route"] = df["Origin_Region"] + "-" + df["Destination_Region"]

    if "Month" not in df.columns and "Ship_Date" in df.columns:
        df["Month"] = df["Ship_Date"].dt.to_period("M").astype(str)

    return df


@st.cache_data
def load_audit_data() -> dict:
    """Load data cleaning audit report if available."""
    audit_file = OUTPUTS_DIR / "data_cleaning_audit.json"
    if audit_file.exists():
        try:
            return json.loads(audit_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


@st.cache_data
def load_business_findings() -> str:
    """Load business findings markdown if available."""
    findings_file = OUTPUTS_DIR / "business_findings.md"
    if findings_file.exists():
        try:
            return findings_file.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


# Load dataset
df_raw = load_processed_data()

# ---------------------------------------------------------
# Sidebar: Controls & Filters
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=400&q=80",
        caption="Logistics Intelligence",
        use_container_width=True,
    )
    st.title("Filters & Settings")

    target_on_time = st.slider(
        "Target On-Time Rate (%)",
        min_value=70.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        help="Benchmark line used across carrier and route comparisons.",
    )

    st.markdown("---")
    st.subheader("Data Slicing")

    # Date Range Filter
    min_date = df_raw["Ship_Date"].dropna().min().date()
    max_date = df_raw["Ship_Date"].dropna().max().date()
    date_range = st.date_input(
        "Ship Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Carrier Filter
    carriers_list = sorted([str(c) for c in df_raw["Carrier"].dropna().unique()])
    selected_carriers = st.multiselect("Carriers", carriers_list, default=carriers_list)

    # Shipping Mode Filter
    modes_list = sorted([str(m) for m in df_raw["Shipping_Mode"].dropna().unique()])
    selected_modes = st.multiselect("Shipping Modes", modes_list, default=modes_list)

    # Priority Filter
    priority_list = sorted([str(p) for p in df_raw["Priority"].dropna().unique()])
    selected_priorities = st.multiselect("Priority Tier", priority_list, default=priority_list)

    # Destination Region Filter
    regions_list = sorted([str(r) for r in df_raw["Destination_Region"].dropna().unique()])
    selected_regions = st.multiselect("Destination Region", regions_list, default=regions_list)

    st.markdown("---")
    st.caption("Supply Chain Delivery Performance Analytics v1.0")

# ---------------------------------------------------------
# Apply Filters
# ---------------------------------------------------------
filtered_df = df_raw.copy()

# Date filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Ship_Date"] >= start_d) & (filtered_df["Ship_Date"] <= end_d)
    ]

# Category filters
if selected_carriers:
    filtered_df = filtered_df[filtered_df["Carrier"].isin(selected_carriers)]
if selected_modes:
    filtered_df = filtered_df[filtered_df["Shipping_Mode"].isin(selected_modes)]
if selected_priorities:
    filtered_df = filtered_df[filtered_df["Priority"].isin(selected_priorities)]
if selected_regions:
    filtered_df = filtered_df[filtered_df["Destination_Region"].isin(selected_regions)]

# Eligible delivered subset for outcome metrics
eligible_df = filtered_df[filtered_df["Outcome_Eligible"] == True].copy()

# ---------------------------------------------------------
# Header & Badges
# ---------------------------------------------------------
st.markdown('<div class="hero-title">Supply Chain Delivery Performance</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Comprehensive operational intelligence for shipment timeliness, carrier scorecards, route bottlenecks, and freight costs.</div>',
    unsafe_allow_html=True,
)

col_b1, col_b2, col_b3 = st.columns([1, 1, 4])
with col_b1:
    st.markdown(f'<span class="badge-pill">Total Records: {len(df_raw):,}</span>', unsafe_allow_html=True)
with col_b2:
    st.markdown(f'<span class="badge-pill">Filtered: {len(filtered_df):,}</span>', unsafe_allow_html=True)
with col_b3:
    st.markdown(f'<span class="badge-pill">Eligible Deliveries: {len(eligible_df):,}</span>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Key Performance Indicator (KPI) Cards
# ---------------------------------------------------------
kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)

total_shipments = len(filtered_df)
on_time_count = int(eligible_df["On_Time"].sum()) if not eligible_df.empty else 0
on_time_rate = (on_time_count / len(eligible_df) * 100) if len(eligible_df) > 0 else 0.0
late_shipments = eligible_df[eligible_df["Delay_Days"] > 0]
avg_delay_late = late_shipments["Delay_Days"].mean() if not late_shipments.empty else 0.0
avg_delivery_days = eligible_df["Delivery_Days"].mean() if not eligible_df.empty else 0.0
avg_cost = filtered_df["Shipping_Cost"].mean() if not filtered_df.empty else 0.0

with kpi_c1:
    st.metric(
        label="On-Time Delivery Rate",
        value=f"{on_time_rate:.1f}%",
        delta=f"{on_time_rate - target_on_time:+.1f}% vs Target",
        delta_color="normal" if on_time_rate >= target_on_time else "inverse",
    )

with kpi_c2:
    st.metric(
        label="Avg. Delivery Duration",
        value=f"{avg_delivery_days:.1f} days",
        delta=f"{eligible_df['Delivery_Days'].median():.1f}d median" if not eligible_df.empty else None,
        delta_color="off",
    )

with kpi_c3:
    st.metric(
        label="Avg. Delay When Late",
        value=f"{avg_delay_late:.1f} days",
        delta=f"{len(late_shipments):,} late shipments",
        delta_color="inverse",
    )

with kpi_c4:
    st.metric(
        label="Average Freight Cost",
        value=f"${avg_cost:,.2f}",
        delta=f"${filtered_df['Shipping_Cost'].median():,.2f} median" if not filtered_df.empty else None,
        delta_color="off",
    )

with kpi_c5:
    cost_per_km = (
        filtered_df["Shipping_Cost"].sum() / filtered_df["Distance_KM"].sum()
        if filtered_df["Distance_KM"].sum() > 0
        else 0.0
    )
    st.metric(
        label="Avg Cost per KM",
        value=f"${cost_per_km:.2f}/km",
        delta=f"{filtered_df['Distance_KM'].mean():.0f} km avg distance" if not filtered_df.empty else None,
        delta_color="off",
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Multi-Tab Dashboard Organization
# ---------------------------------------------------------
tab_overview, tab_carriers, tab_delays, tab_costs, tab_explorer, tab_findings = st.tabs(
    [
        "📊 Executive Overview",
        "🚚 Carrier & Route Scorecards",
        "⚠️ Delay & Root Causes",
        "💰 Freight Cost Efficiency",
        "🔍 Shipment Explorer",
        "📋 Quality Audit & Report",
    ]
)

# ---------------------------------------------------------
# TAB 1: Executive Overview
# ---------------------------------------------------------
with tab_overview:
    col_t1_left, col_t1_right = st.columns([1, 2])

    with col_t1_left:
        st.subheader("On-Time vs Late Deliveries")
        if not eligible_df.empty:
            status_counts = pd.DataFrame(
                {
                    "Status": ["On-Time", "Late"],
                    "Count": [on_time_count, len(eligible_df) - on_time_count],
                }
            )
            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.6,
                color="Status",
                color_discrete_map={"On-Time": "#10B981", "Late": "#EF4444"},
            )
            fig_donut.update_traces(textposition="inside", textinfo="percent+label")
            fig_donut.update_layout(
                showlegend=False,
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No eligible deliveries match current filters.")

    with col_t1_right:
        st.subheader("Monthly Performance Trends")
        if not eligible_df.empty and "Month" in eligible_df.columns:
            monthly_perf = (
                eligible_df.groupby("Month")
                .agg(
                    Total=("Shipment_ID", "count"),
                    On_Time_Rate=("On_Time", lambda s: s.mean() * 100),
                    Avg_Delay=("Delay_Days", "mean"),
                )
                .reset_index()
                .sort_values("Month")
            )

            fig_trend = go.Figure()
            # Bar for shipment volume
            fig_trend.add_trace(
                go.Bar(
                    x=monthly_perf["Month"],
                    y=monthly_perf["Total"],
                    name="Shipment Volume",
                    marker_color="rgba(59, 130, 246, 0.4)",
                    yaxis="y2",
                )
            )
            # Line for On-Time Rate
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_perf["Month"],
                    y=monthly_perf["On_Time_Rate"],
                    name="On-Time Rate (%)",
                    mode="lines+markers",
                    line=dict(color="#10B981", width=3),
                )
            )
            # Benchmark Line
            fig_trend.add_hline(
                y=target_on_time,
                line_dash="dot",
                line_color="#F59E0B",
                annotation_text=f"Target ({target_on_time:.0f}%)",
                annotation_position="bottom right",
            )
            fig_trend.update_layout(
                yaxis=dict(title="On-Time Rate (%)", range=[0, 100]),
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=320,
                margin=dict(t=20, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    # Destination Region Performance
    st.subheader("Performance by Destination Region")
    if not eligible_df.empty:
        region_perf = (
            eligible_df.groupby("Destination_Region")
            .agg(
                Shipments=("Shipment_ID", "count"),
                On_Time_Rate=("On_Time", lambda s: s.mean() * 100),
                Avg_Delay=("Delay_Days", "mean"),
            )
            .reset_index()
            .sort_values("On_Time_Rate", ascending=False)
        )

        fig_region = px.bar(
            region_perf,
            x="Destination_Region",
            y="On_Time_Rate",
            color="On_Time_Rate",
            color_continuous_scale="Viridis",
            text=region_perf["On_Time_Rate"].apply(lambda v: f"{v:.1f}%"),
            hover_data=["Shipments", "Avg_Delay"],
            labels={"Destination_Region": "Region", "On_Time_Rate": "On-Time Rate (%)"},
        )
        fig_region.add_hline(y=target_on_time, line_dash="dash", line_color="#EF4444")
        fig_region.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_region, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: Carrier & Route Scorecards
# ---------------------------------------------------------
with tab_carriers:
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        st.subheader("Carrier On-Time Benchmark")
        if not eligible_df.empty:
            carrier_summary = (
                eligible_df.groupby("Carrier")
                .agg(
                    Shipments=("Shipment_ID", "count"),
                    On_Time_Rate=("On_Time", lambda s: s.mean() * 100),
                    Avg_Delay=("Delay_Days", "mean"),
                    Avg_Delay_Among_Late=("Delay_Days", lambda s: s[s > 0].mean()),
                    Avg_Cost=("Shipping_Cost", "mean"),
                )
                .reset_index()
                .sort_values("On_Time_Rate", ascending=True)
            )

            fig_carrier = px.bar(
                carrier_summary,
                x="On_Time_Rate",
                y="Carrier",
                orientation="h",
                text=carrier_summary["On_Time_Rate"].apply(lambda x: f"{x:.1f}%"),
                color="On_Time_Rate",
                color_continuous_scale="RdYlGn",
                labels={"On_Time_Rate": "On-Time Rate (%)"},
            )
            fig_carrier.add_vline(x=target_on_time, line_dash="dash", line_color="#F59E0B")
            fig_carrier.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_carrier, use_container_width=True)

    with c_col2:
        st.subheader("Average Late Days by Carrier")
        if not eligible_df.empty:
            fig_delay_c = px.bar(
                carrier_summary.sort_values("Avg_Delay_Among_Late", ascending=False),
                x="Carrier",
                y="Avg_Delay_Among_Late",
                color="Avg_Delay_Among_Late",
                color_continuous_scale="Oranges",
                text=carrier_summary["Avg_Delay_Among_Late"].apply(lambda x: f"{x:.2f}d"),
                labels={"Avg_Delay_Among_Late": "Avg Delay When Late (Days)"},
            )
            fig_delay_c.update_layout(height=360, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_delay_c, use_container_width=True)

    st.subheader("Corridor & Route Watchlist")
    if not eligible_df.empty and "Route" in eligible_df.columns:
        route_summary = (
            eligible_df.groupby("Route")
            .agg(
                Shipments=("Shipment_ID", "count"),
                On_Time_Rate=("On_Time", lambda s: s.mean() * 100),
                Avg_Delay=("Delay_Days", "mean"),
                Avg_Delay_Among_Late=("Delay_Days", lambda s: s[s > 0].mean()),
            )
            .reset_index()
        )
        # Filter for statistically relevant volume
        min_vol = st.slider("Minimum Route Shipment Volume Filter", 1, 50, 20)
        route_summary_filtered = route_summary[route_summary["Shipments"] >= min_vol]

        r_sub1, r_sub2 = st.columns(2)
        with r_sub1:
            st.markdown("**Bottom 5 Routes (Lowest On-Time Rate)**")
            bottom_routes = route_summary_filtered.sort_values("On_Time_Rate").head(5)
            st.dataframe(
                bottom_routes.style.format(
                    {"On_Time_Rate": "{:.1f}%", "Avg_Delay": "{:.2f}d", "Avg_Delay_Among_Late": "{:.2f}d"}
                ),
                use_container_width=True,
            )

        with r_sub2:
            st.markdown("**Top 5 Routes (Highest On-Time Rate)**")
            top_routes = route_summary_filtered.sort_values("On_Time_Rate", ascending=False).head(5)
            st.dataframe(
                top_routes.style.format(
                    {"On_Time_Rate": "{:.1f}%", "Avg_Delay": "{:.2f}d", "Avg_Delay_Among_Late": "{:.2f}d"}
                ),
                use_container_width=True,
            )

# ---------------------------------------------------------
# TAB 3: Delay & Root Causes
# ---------------------------------------------------------
with tab_delays:
    d_col1, d_col2 = st.columns(2)

    with d_col1:
        st.subheader("Late Shipments by Reason Category")
        late_only = eligible_df[eligible_df["Delay_Days"] > 0]
        if not late_only.empty:
            reason_counts = (
                late_only["Delay_Reason"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Delay_Reason", "count": "Shipments"})
            )
            fig_reason = px.bar(
                reason_counts,
                x="Delay_Reason",
                y="Shipments",
                color="Shipments",
                color_continuous_scale="Reds",
                text="Shipments",
                labels={"Delay_Reason": "Reason", "Shipments": "Shipments Delayed"},
            )
            fig_reason.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_reason, use_container_width=True)
        else:
            st.info("No late shipments found under current filters.")

    with d_col2:
        st.subheader("Delay Days Distribution")
        if not eligible_df.empty:
            fig_dist = px.histogram(
                eligible_df,
                x="Delay_Days",
                nbins=25,
                color="On_Time",
                color_discrete_map={1: "#10B981", 0: "#EF4444"},
                labels={"Delay_Days": "Delay Days (Negative = Early, 0 = On Time, Positive = Late)", "On_Time": "On-Time"},
            )
            fig_dist.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_dist, use_container_width=True)

    st.subheader("Distance vs. Delay Correlation")
    if not eligible_df.empty:
        fig_scatter = px.scatter(
            eligible_df.sample(min(1000, len(eligible_df)), random_state=42),
            x="Distance_KM",
            y="Delay_Days",
            color="Shipping_Mode",
            opacity=0.6,
            labels={"Distance_KM": "Distance (KM)", "Delay_Days": "Delay (Days)"},
        )
        fig_scatter.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: Freight Cost Efficiency
# ---------------------------------------------------------
with tab_costs:
    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.subheader("Average Cost per KM by Shipping Mode")
        mode_cost = (
            filtered_df.groupby("Shipping_Mode")
            .agg(
                Shipments=("Shipment_ID", "count"),
                Avg_Cost=("Shipping_Cost", "mean"),
                Avg_Dist=("Distance_KM", "mean"),
                Total_Cost=("Shipping_Cost", "sum"),
                Total_Dist=("Distance_KM", "sum"),
            )
            .reset_index()
        )
        mode_cost["Cost_Per_KM"] = mode_cost["Total_Cost"] / mode_cost["Total_Dist"]

        fig_cpk = px.bar(
            mode_cost,
            x="Shipping_Mode",
            y="Cost_Per_KM",
            text=mode_cost["Cost_Per_KM"].apply(lambda v: f"${v:.2f}/km"),
            color="Shipping_Mode",
            color_discrete_sequence=px.colors.qualitative.Prism,
            labels={"Cost_Per_KM": "Cost per KM ($)", "Shipping_Mode": "Mode"},
        )
        fig_cpk.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_cpk, use_container_width=True)

    with cost_col2:
        st.subheader("Delivery Speed vs. Cost by Mode")
        fig_box = px.box(
            eligible_df,
            x="Shipping_Mode",
            y="Delivery_Days",
            color="Shipping_Mode",
            labels={"Delivery_Days": "Delivery Duration (Days)", "Shipping_Mode": "Mode"},
        )
        fig_box.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: Shipment Explorer
# ---------------------------------------------------------
with tab_explorer:
    st.subheader("Search & Export Shipments")
    search_q = st.text_input("Search Shipment ID", "")

    display_df = filtered_df.copy()
    if search_q.strip():
        display_df = display_df[display_df["Shipment_ID"].str.contains(search_q.strip(), case=False, na=False)]

    columns_to_show = [
        "Shipment_ID",
        "Carrier",
        "Route",
        "Shipping_Mode",
        "Priority",
        "Ship_Date",
        "Expected_Delivery",
        "Actual_Delivery",
        "Delay_Days",
        "On_Time",
        "Delay_Reason",
        "Shipping_Cost",
    ]
    columns_to_show = [c for c in columns_to_show if c in display_df.columns]

    st.dataframe(
        display_df[columns_to_show].head(500),
        use_container_width=True,
        height=400,
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Shipments CSV",
        data=csv_data,
        file_name="filtered_shipments.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# TAB 6: Quality Audit & Executive Report
# ---------------------------------------------------------
with tab_findings:
    q_col1, q_col2 = st.columns([1, 1])

    with q_col1:
        st.subheader("Data Cleaning & Quality Audit")
        audit = load_audit_data()
        if audit:
            st.json(audit)
        else:
            st.info("Run `python main.py` to generate the complete data cleaning audit log.")

    with q_col2:
        st.subheader("Executive Findings & Recommendations")
        report_text = load_business_findings()
        if report_text:
            st.markdown(report_text)
        else:
            st.info("Run `python main.py` to generate the executive report in `outputs/business_findings.md`.")
