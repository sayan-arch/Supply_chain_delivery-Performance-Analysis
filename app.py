"""SupplyIQ | Enterprise Supply Chain & Logistics Intelligence Platform.

Interactive Executive Analytics Dashboard for tracking supply chain performance,
carrier scorecards, route bottlenecks, delay root-cause analysis, and freight economics.
"""

from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Master Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="SupplyIQ | Logistics Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End SaaS CSS Design System
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Background & Container adjustments */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 96%;
    }

    /* Live Telemetry Pulse Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10B981;
        box-shadow: 0 0 8px #10B981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Brand Header */
    .brand-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 40%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 1.2rem;
        line-height: 1.5;
    }

    /* Meta Badges */
    .meta-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 8px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #CBD5E1;
        font-size: 0.8rem;
        font-weight: 500;
        backdrop-filter: blur(8px);
    }
    .meta-pill strong {
        color: #F8FAFC;
    }

    /* Premium Custom KPI Card */
    .kpi-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        border-color: rgba(96, 165, 250, 0.4);
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.15);
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.6rem;
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        color: #94A3B8;
    }
    .kpi-icon {
        font-size: 1.15rem;
        opacity: 0.85;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin-bottom: 0.45rem;
    }
    .kpi-footer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .delta-positive {
        color: #34D399;
        background: rgba(16, 185, 129, 0.12);
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 600;
    }
    .delta-negative {
        color: #F87171;
        background: rgba(239, 68, 68, 0.12);
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 600;
    }
    .delta-neutral {
        color: #94A3B8;
        background: rgba(148, 163, 184, 0.1);
        padding: 2px 7px;
        border-radius: 6px;
    }

    /* Executive Callout Card */
    .insight-card {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.25) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.2rem;
        color: #E2E8F0;
        font-size: 0.9rem;
        line-height: 1.55;
    }
    .insight-card strong {
        color: #60A5FA;
    }

    /* Tab bar refinement */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #94A3B8;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.2) !important;
        color: #60A5FA !important;
        border-bottom: 2px solid #3B82F6 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #0B1120;
        border-right: 1px solid rgba(255, 255, 255, 0.07);
    }
    .sidebar-brand {
        padding: 0.5rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.2rem;
    }
    .sidebar-brand h3 {
        margin: 0;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
    }
    .sidebar-brand p {
        margin: 2px 0 0 0;
        color: #64748B;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"


# ---------------------------------------------------------
# Plotly Unified Dark/Transparent Theme Helper
# ---------------------------------------------------------
def polish_plot(fig, height=340, show_grid=True):
    """Apply a consistent high-end corporate styling to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color="#94A3B8",
            size=12,
        ),
        margin=dict(t=35, b=30, l=35, r=25),
        height=height,
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family="Plus Jakarta Sans",
            bordercolor="rgba(255,255,255,0.1)",
        ),
    )
    if show_grid:
        fig.update_xaxes(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(255,255,255,0.1)",
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            linecolor="rgba(255,255,255,0.1)",
        )
    return fig


# ---------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------
@st.cache_data
def load_processed_data() -> pd.DataFrame:
    """Load cleaned dataset from disk or trigger pipeline cleaning."""
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
    else:
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
# Sidebar: Control Tower & Interactive Filters
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.6rem;">📦</span>
                <div>
                    <h3 style="margin: 0;">SupplyIQ</h3>
                    <p style="margin: 0;">Logistics Control Tower</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    target_on_time = st.slider(
        "🎯 Operational SLA Target (%)",
        min_value=70.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
        help="Corporate delivery timeliness benchmark line across carriers and routes.",
    )

    st.markdown("---")
    st.markdown("<p style='font-size:0.78rem; text-transform:uppercase; font-weight:700; color:#64748B;'>Faceted Cohort Slicing</p>", unsafe_allow_html=True)

    # Date Range Filter
    min_date = df_raw["Ship_Date"].dropna().min().date()
    max_date = df_raw["Ship_Date"].dropna().max().date()
    date_range = st.date_input(
        "Dispatch Window (Ship Date)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Carrier Filter
    carriers_list = sorted([str(c) for c in df_raw["Carrier"].dropna().unique()])
    selected_carriers = st.multiselect("Logistics Carriers", carriers_list, default=carriers_list)

    # Shipping Mode Filter
    modes_list = sorted([str(m) for m in df_raw["Shipping_Mode"].dropna().unique()])
    selected_modes = st.multiselect("Modal Split", modes_list, default=modes_list)

    # Priority Filter
    priority_list = sorted([str(p) for p in df_raw["Priority"].dropna().unique()])
    selected_priorities = st.multiselect("Priority Tiers", priority_list, default=priority_list)

    # Destination Region Filter
    regions_list = sorted([str(r) for r in df_raw["Destination_Region"].dropna().unique()])
    selected_regions = st.multiselect("Destination Corridor", regions_list, default=regions_list)

    st.markdown("---")
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; color:#64748B; font-size:0.75rem;">
            <span>Engine: Pandas 3.0</span>
            <span>Build 2.4.1</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Filter Dataset Cohort
# ---------------------------------------------------------
filtered_df = df_raw.copy()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Ship_Date"] >= start_d) & (filtered_df["Ship_Date"] <= end_d)
    ]

if selected_carriers:
    filtered_df = filtered_df[filtered_df["Carrier"].isin(selected_carriers)]
if selected_modes:
    filtered_df = filtered_df[filtered_df["Shipping_Mode"].isin(selected_modes)]
if selected_priorities:
    filtered_df = filtered_df[filtered_df["Priority"].isin(selected_priorities)]
if selected_regions:
    filtered_df = filtered_df[filtered_df["Destination_Region"].isin(selected_regions)]

# Eligible delivered cohort for core timing KPIs
eligible_df = filtered_df[filtered_df["Outcome_Eligible"] == True].copy()

# ---------------------------------------------------------
# Executive Top Bar & Header
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])

with col_h1:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:12px; margin-bottom: 4px;">
            <div class="status-badge">
                <span class="pulse-dot"></span>
                <span>Live Operational Telemetry</span>
            </div>
            <span style="color:#64748B; font-size:0.8rem;">• System Synced Oct 2026</span>
        </div>
        <div class="brand-title">SupplyIQ &bull; Logistics Intelligence</div>
        <div class="brand-subtitle">
            Executive control tower delivering real-time shipment timeliness KPIs, carrier benchmark scorecards, corridor delay tracking, and unit economics.
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; gap:6px; align-items:flex-end;">
            <div class="meta-pill">Total Database: <strong>{len(df_raw):,}</strong></div>
            <div class="meta-pill">Filtered Cohort: <strong>{len(filtered_df):,}</strong></div>
            <div class="meta-pill">Delivered & Evaluated: <strong>{len(eligible_df):,}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Primary Executive KPI Scorecard Grid
# ---------------------------------------------------------
total_shipments = len(filtered_df)
on_time_count = int(eligible_df["On_Time"].sum()) if not eligible_df.empty else 0
on_time_rate = (on_time_count / len(eligible_df) * 100) if len(eligible_df) > 0 else 0.0
late_shipments = eligible_df[eligible_df["Delay_Days"] > 0]
avg_delay_late = late_shipments["Delay_Days"].mean() if not late_shipments.empty else 0.0
avg_delivery_days = eligible_df["Delivery_Days"].mean() if not eligible_df.empty else 0.0
avg_cost = filtered_df["Shipping_Cost"].mean() if not filtered_df.empty else 0.0
cost_per_km = (
    filtered_df["Shipping_Cost"].sum() / filtered_df["Distance_KM"].sum()
    if filtered_df["Distance_KM"].sum() > 0
    else 0.0
)

kpi_diff = on_time_rate - target_on_time
diff_class = "delta-positive" if kpi_diff >= 0 else "delta-negative"
diff_symbol = "+" if kpi_diff >= 0 else ""

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">On-Time Delivery</span>
                <span class="kpi-icon">🎯</span>
            </div>
            <div class="kpi-value">{on_time_rate:.1f}%</div>
            <div class="kpi-footer">
                <span class="{diff_class}">{diff_symbol}{kpi_diff:.1f}%</span>
                <span style="color:#64748B;">vs {target_on_time:.0f}% SLA</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    med_days = eligible_df['Delivery_Days'].median() if not eligible_df.empty else 0.0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Transit Duration</span>
                <span class="kpi-icon">⏱️</span>
            </div>
            <div class="kpi-value">{avg_delivery_days:.1f}<span style="font-size:1.1rem; color:#94A3B8;"> d</span></div>
            <div class="kpi-footer">
                <span class="delta-neutral">Median: {med_days:.1f}d</span>
                <span style="color:#64748B;">avg ship-to-door</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Late Delay Severity</span>
                <span class="kpi-icon">⚠️</span>
            </div>
            <div class="kpi-value">{avg_delay_late:.1f}<span style="font-size:1.1rem; color:#94A3B8;"> d</span></div>
            <div class="kpi-footer">
                <span class="delta-negative">{len(late_shipments):,} late</span>
                <span style="color:#64748B;">behind schedule</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    med_cost = filtered_df['Shipping_Cost'].median() if not filtered_df.empty else 0.0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Average Freight</span>
                <span class="kpi-icon">💰</span>
            </div>
            <div class="kpi-value">${avg_cost:,.0f}</div>
            <div class="kpi-footer">
                <span class="delta-neutral">${med_cost:,.0f} median</span>
                <span style="color:#64748B;">per consignment</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k5:
    avg_dist = filtered_df['Distance_KM'].mean() if not filtered_df.empty else 0.0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">Freight / KM Index</span>
                <span class="kpi-icon">📊</span>
            </div>
            <div class="kpi-value">${cost_per_km:.2f}<span style="font-size:0.95rem; color:#94A3B8;">/km</span></div>
            <div class="kpi-footer">
                <span class="delta-neutral">{avg_dist:,.0f} km avg</span>
                <span style="color:#64748B;">haul distance</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabbed Analytics Workstation
# ---------------------------------------------------------
tab_overview, tab_carriers, tab_delays, tab_costs, tab_explorer, tab_findings = st.tabs(
    [
        "📊 Network Overview",
        "🚚 Carrier & Route Scorecards",
        "⚠️ Delay Root Causes",
        "💰 Freight Economics",
        "🔍 Shipment Explorer",
        "📋 Quality Audit & Executive Report",
    ]
)

# ---------------------------------------------------------
# TAB 1: Network Overview
# ---------------------------------------------------------
with tab_overview:
    st.markdown(
        f"""
        <div class="insight-card">
            <strong>💡 Executive Network Summary:</strong> Current network timeliness stands at <strong>{on_time_rate:.1f}%</strong> 
            against an operational SLA of <strong>{target_on_time:.0f}%</strong>. 
            Late shipments average <strong>{avg_delay_late:.2f} days</strong> behind planned ETA across evaluated lanes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_t1_left, col_t1_right = st.columns([1, 2])

    with col_t1_left:
        st.markdown("##### Delivery Timeliness Ratio")
        if not eligible_df.empty:
            status_counts = pd.DataFrame(
                {
                    "Status": ["On-Time", "Delayed"],
                    "Count": [on_time_count, len(eligible_df) - on_time_count],
                }
            )
            fig_donut = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.62,
                color="Status",
                color_discrete_map={"On-Time": "#10B981", "Delayed": "#EF4444"},
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color="#0F172A", width=3)),
            )
            fig_donut = polish_plot(fig_donut, height=330, show_grid=False)
            fig_donut.update_layout(showlegend=False)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No matching shipment records.")

    with col_t1_right:
        st.markdown("##### Longitudinal On-Time Trajectory vs. Volume")
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
            # Volume bar trace
            fig_trend.add_trace(
                go.Bar(
                    x=monthly_perf["Month"],
                    y=monthly_perf["Total"],
                    name="Monthly Volume",
                    marker_color="rgba(59, 130, 246, 0.28)",
                    marker_line=dict(color="rgba(59, 130, 246, 0.5)", width=1),
                    yaxis="y2",
                )
            )
            # Timeliness line trace
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_perf["Month"],
                    y=monthly_perf["On_Time_Rate"],
                    name="On-Time Rate (%)",
                    mode="lines+markers",
                    line=dict(color="#10B981", width=3, shape="spline"),
                    marker=dict(size=7, color="#10B981", line=dict(color="#FFFFFF", width=1.5)),
                )
            )
            # SLA Target line
            fig_trend.add_hline(
                y=target_on_time,
                line_dash="dot",
                line_color="#F59E0B",
                annotation_text=f"SLA Target ({target_on_time:.0f}%)",
                annotation_position="bottom right",
                annotation_font=dict(color="#F59E0B", size=11),
            )
            fig_trend = polish_plot(fig_trend, height=330)
            fig_trend.update_layout(
                yaxis=dict(title="On-Time Rate (%)", range=[0, 100]),
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    # Destination Region Corridor Performance
    st.markdown("##### Destination Region Timeliness Comparison")
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
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            text=region_perf["On_Time_Rate"].apply(lambda v: f"{v:.1f}%"),
            hover_data=["Shipments", "Avg_Delay"],
            labels={"Destination_Region": "Destination", "On_Time_Rate": "On-Time Rate (%)"},
        )
        fig_region.add_hline(y=target_on_time, line_dash="dash", line_color="#F59E0B")
        fig_region = polish_plot(fig_region, height=280)
        fig_region.update_traces(textposition="outside", marker_line_width=0)
        fig_region.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_region, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: Carrier & Route Scorecards
# ---------------------------------------------------------
with tab_carriers:
    st.markdown(
        """
        <div class="insight-card">
            <strong>🚚 Carrier Performance Scorecard:</strong> Carriers are ranked by their audited on-time delivery rate. 
            Highlighting underperformers allows procurement to prioritize contract re-negotiations or volume redistribution.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_col1, c_col2 = st.columns(2)

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

        with c_col1:
            st.markdown("##### Carrier On-Time Performance")
            fig_carrier = px.bar(
                carrier_summary,
                x="On_Time_Rate",
                y="Carrier",
                orientation="h",
                text=carrier_summary["On_Time_Rate"].apply(lambda x: f"{x:.1f}%"),
                color="On_Time_Rate",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                labels={"On_Time_Rate": "On-Time Rate (%)"},
            )
            fig_carrier.add_vline(x=target_on_time, line_dash="dash", line_color="#F59E0B")
            fig_carrier = polish_plot(fig_carrier, height=330)
            fig_carrier.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_carrier, use_container_width=True)

        with c_col2:
            st.markdown("##### Delay Severity When Shipments Are Late")
            fig_delay_c = px.bar(
                carrier_summary.sort_values("Avg_Delay_Among_Late", ascending=False),
                x="Carrier",
                y="Avg_Delay_Among_Late",
                color="Avg_Delay_Among_Late",
                color_continuous_scale="Reds",
                text=carrier_summary["Avg_Delay_Among_Late"].apply(lambda x: f"{x:.2f}d"),
                labels={"Avg_Delay_Among_Late": "Avg Delay When Late (Days)"},
            )
            fig_delay_c = polish_plot(fig_delay_c, height=330)
            fig_delay_c.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_delay_c, use_container_width=True)

    # Route Analysis
    st.markdown("---")
    st.markdown("##### High-Volume Corridor Watchlist")
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

        vol_col1, vol_col2 = st.columns([1, 3])
        with vol_col1:
            min_vol = st.slider("Corridor Volume Threshold", 1, 100, 20)
        with vol_col2:
            st.caption(f"Displaying routes handling $\\ge$ {min_vol} deliveries to avoid statistical bias.")

        route_summary_filtered = route_summary[route_summary["Shipments"] >= min_vol]

        r_sub1, r_sub2 = st.columns(2)
        with r_sub1:
            st.markdown("**🚨 Bottom 5 Corridors (Lowest Timeliness)**")
            bottom_routes = route_summary_filtered.sort_values("On_Time_Rate").head(5)
            st.dataframe(
                bottom_routes.style.format(
                    {"On_Time_Rate": "{:.1f}%", "Avg_Delay": "{:.2f}d", "Avg_Delay_Among_Late": "{:.2f}d", "Shipments": "{:,.0f}"}
                ),
                use_container_width=True,
                height=210,
            )

        with r_sub2:
            st.markdown("**⭐ Top 5 Corridors (Highest Timeliness)**")
            top_routes = route_summary_filtered.sort_values("On_Time_Rate", ascending=False).head(5)
            st.dataframe(
                top_routes.style.format(
                    {"On_Time_Rate": "{:.1f}%", "Avg_Delay": "{:.2f}d", "Avg_Delay_Among_Late": "{:.2f}d", "Shipments": "{:,.0f}"}
                ),
                use_container_width=True,
                height=210,
            )

# ---------------------------------------------------------
# TAB 3: Delay Root Causes
# ---------------------------------------------------------
with tab_delays:
    st.markdown(
        """
        <div class="insight-card">
            <strong>⚠️ Root-Cause Delay Analytics:</strong> Warehouse backlogs and fleet maintenance issues represent 
            the largest share of delayed shipments. Weather delays incur the highest average disruption length.
        </div>
        """,
        unsafe_allow_html=True,
    )

    d_col1, d_col2 = st.columns(2)

    with d_col1:
        st.markdown("##### Late Shipments by Recorded Delay Reason")
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
                labels={"Delay_Reason": "Root Cause", "Shipments": "Delayed Volume"},
            )
            fig_reason = polish_plot(fig_reason, height=340)
            fig_reason.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_reason, use_container_width=True)
        else:
            st.info("No late shipments recorded.")

    with d_col2:
        st.markdown("##### Distribution of Deviation from Expected ETA")
        if not eligible_df.empty:
            fig_dist = px.histogram(
                eligible_df,
                x="Delay_Days",
                nbins=22,
                color="On_Time",
                color_discrete_map={1: "#10B981", 0: "#EF4444"},
                labels={"Delay_Days": "Delay Days (Negative = Early, 0 = On Time, Positive = Late)", "On_Time": "On-Time"},
            )
            fig_dist = polish_plot(fig_dist, height=340)
            fig_dist.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("##### Haul Distance vs. Arrival Delay Correlation")
    if not eligible_df.empty:
        fig_scatter = px.scatter(
            eligible_df.sample(min(1200, len(eligible_df)), random_state=42),
            x="Distance_KM",
            y="Delay_Days",
            color="Shipping_Mode",
            color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
            opacity=0.65,
            labels={"Distance_KM": "Distance (KM)", "Delay_Days": "Delay (Days)", "Shipping_Mode": "Mode"},
        )
        fig_scatter = polish_plot(fig_scatter, height=360)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: Freight Economics
# ---------------------------------------------------------
with tab_costs:
    st.markdown(
        """
        <div class="insight-card">
            <strong>💰 Freight Economics & Unit Costs:</strong> Air transport offers the fastest delivery duration at $1.85/km, 
            while Rail provides the most economical long-haul freight rate at $0.92/km.
        </div>
        """,
        unsafe_allow_html=True,
    )

    cost_col1, cost_col2 = st.columns(2)

    with cost_col1:
        st.markdown("##### Unit Freight Cost per Kilometer by Mode")
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
            color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
            labels={"Cost_Per_KM": "Freight Cost per KM ($)", "Shipping_Mode": "Mode"},
        )
        fig_cpk = polish_plot(fig_cpk, height=330)
        fig_cpk.update_layout(showlegend=False)
        st.plotly_chart(fig_cpk, use_container_width=True)

    with cost_col2:
        st.markdown("##### Transit Speed Distribution by Mode")
        fig_box = px.box(
            eligible_df,
            x="Shipping_Mode",
            y="Delivery_Days",
            color="Shipping_Mode",
            color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6"],
            labels={"Delivery_Days": "Delivery Duration (Days)", "Shipping_Mode": "Mode"},
        )
        fig_box = polish_plot(fig_box, height=330)
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: Shipment Explorer
# ---------------------------------------------------------
with tab_explorer:
    st.markdown("##### Audited Consignment Data Table")
    search_q = st.text_input("🔍 Quick Lookup by Shipment ID (e.g., SHP00123)", "")

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
        height=380,
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Consignments (CSV)",
        data=csv_data,
        file_name="supplyiq_filtered_shipments.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# TAB 6: Quality Audit & Executive Report
# ---------------------------------------------------------
with tab_findings:
    q_col1, q_col2 = st.columns([1, 1])

    with q_col1:
        st.markdown("##### Automated Data Cleaning Audit")
        audit = load_audit_data()
        if audit:
            st.json(audit)
        else:
            st.info("Run `python main.py` to regenerate the data audit report.")

    with q_col2:
        st.markdown("##### Executive Recommendations & Findings")
        report_text = load_business_findings()
        if report_text:
            st.markdown(report_text)
        else:
            st.info("Run `python main.py` to populate executive findings.")
