"""
StockSense360: Retail Replenishment Control Tower
Streamlit App — built for CA_1 pilot data (M5 Forecasting dataset)

Run:
    pip install streamlit pandas plotly
    streamlit run app.py
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

# Auto refresh every 5 minutes (300000 milliseconds)
st_autorefresh(interval=300000, key="autorefresh")
st.set_page_config(
    page_title="StockSense360 | Control Tower",
    page_icon="📦",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; color: #e0e0e0; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #1a1d27; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1e2130;
        border: 1px solid #2e3250;
        border-radius: 10px;
        padding: 16px;
    }

    /* Priority badge colors */
    .badge-high   { background:#C0392B; color:#fff; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px; }
    .badge-medium { background:#E67E22; color:#fff; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px; }
    .badge-low    { background:#27AE60; color:#fff; padding:3px 10px; border-radius:12px; font-weight:600; font-size:12px; }

    /* Section headers */
    .section-header {
        font-size:18px; font-weight:700; color:#7c83ff;
        border-bottom: 1px solid #2e3250; padding-bottom:6px; margin-bottom:12px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
BASE = Path(__file__).parent

@st.cache_data
def load_data():
    # Try loading from same folder as app.py, else from 02_data_processed / 08_outputs
    paths_sales = [
        BASE / "fact_sales.csv",
        BASE.parent / "02_data_processed" / "fact_sales.csv",
    ]
    paths_action = [
        BASE / "control_tower_actionlist_CA1.csv",
        BASE.parent / "08_outputs" / "control_tower_actionlist_CA1.csv",
    ]
    paths_forecast = [
        BASE / "forecast_14days_store_CA1.csv",
        BASE.parent / "08_outputs" / "forecast_14days_store_CA1.csv",
    ]
    paths_product = [
        BASE / "dim_product.csv",
        BASE.parent / "02_data_processed" / "dim_product.csv",
    ]

    def find_file(paths):
        for p in paths:
            if p.exists():
                return p
        return None

    sales_path   = find_file(paths_sales)
    action_path  = find_file(paths_action)
    fore_path    = find_file(paths_forecast)
    prod_path    = find_file(paths_product)

    errors = []
    if not action_path:  errors.append("control_tower_actionlist_CA1.csv")
    if not fore_path:    errors.append("forecast_14days_store_CA1.csv")
    if not prod_path:    errors.append("dim_product.csv")

    if errors:
        return None, None, None, None, errors

    # sales is optional - may be too large for cloud deployment
    sales = pd.read_csv(sales_path, parse_dates=["date"]) if sales_path else pd.DataFrame(columns=["date","store_id","item_id","units_sold","cat_id"])
    action  = pd.read_csv(action_path)
    fore    = pd.read_csv(fore_path,   parse_dates=["date"])
    product = pd.read_csv(prod_path)

    # Enrich action list with cat_id from dim_product
    if "cat_id" not in action.columns:
        action = action.merge(product[["item_id","cat_id","dept_id"]], on="item_id", how="left")

    return sales, action, fore, product, []

sales_df, action_df, fore_df, product_df, load_errors = load_data()

# ─────────────────────────────────────────────
# ERROR STATE
# ─────────────────────────────────────────────
if load_errors:
    st.error(f"❌ Missing files: {', '.join(load_errors)}")
    st.info(
        "Place these files in the **same folder as app.py**:\n\n"
        "- `fact_sales.csv`\n"
        "- `control_tower_actionlist_CA1.csv`\n"
        "- `forecast_14days_store_CA1.csv`\n"
        "- `dim_product.csv`"
    )
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/48/box.png", width=48)
st.sidebar.title("StockSense360")
st.sidebar.caption("Retail Replenishment Control Tower")
st.sidebar.markdown("---")

# Category filter
all_cats = sorted(action_df["cat_id"].dropna().unique().tolist())
sel_cat = st.sidebar.selectbox("📂 Category", ["All"] + all_cats)

# Priority Tier filter
all_tiers = ["All", "High", "Medium", "Low"]
sel_tier = st.sidebar.selectbox("🚨 Priority Tier", all_tiers)

# Store filter (only CA_1 in pilot, but ready for scale)
all_stores = sorted(action_df["store_id"].unique().tolist())
sel_store = st.sidebar.selectbox("🏪 Store", ["All"] + all_stores)

st.sidebar.markdown("---")
st.sidebar.caption("📊 Data: Kaggle M5 Forecasting (Walmart-style retail)")
st.sidebar.caption("🗓️ Forecast horizon: 14 days from 2016-04-25")

# Apply filters to action list
filtered = action_df.copy()
if sel_cat   != "All": filtered = filtered[filtered["cat_id"]   == sel_cat]
if sel_tier  != "All": filtered = filtered[filtered["priority_tier"] == sel_tier]
if sel_store != "All": filtered = filtered[filtered["store_id"] == sel_store]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 📦 StockSense360 — Control Tower")
st.markdown("**Store CA_1 · Pilot: 41 SKUs · M5 Forecasting Dataset**")
st.markdown("---")

# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
needs_reorder = action_df[action_df["suggested_order_qty_forecast"] > 0]
high_priority = action_df[action_df["priority_tier"] == "High"]
total_units   = action_df["suggested_order_qty_forecast"].sum()
avg_score     = action_df["priority_score"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("🔴 SKUs Needing Reorder",  f"{len(needs_reorder)}", f"of {len(action_df)} total SKUs")
k2.metric("⚡ High Priority Items",   f"{len(high_priority)}", "Immediate action needed")
k3.metric("📦 Total Units to Order",  f"{int(total_units)}", "Across all SKUs")
k4.metric("📊 Avg Priority Score",    f"{avg_score:.1f}", "out of 100")

st.markdown("---")

# ─────────────────────────────────────────────
# TAB LAYOUT
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🏆 Action List", "📈 Sales & Forecast", "📋 Full Data Explorer"])

# ══════════════════════════════════════════════
# TAB 1 — ACTION LIST (Control Tower)
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-header">🔴 Priority Reorder Action List</div>', unsafe_allow_html=True)

    # Top 10 priority chart
    top15 = action_df.nlargest(15, "priority_score")
    color_map = {"High": "#C0392B", "Medium": "#E67E22", "Low": "#27AE60"}

    fig_bar = px.bar(
        top15,
        x="priority_score",
        y="item_id",
        orientation="h",
        color="priority_tier",
        color_discrete_map=color_map,
        title="Top 15 Priority Items",
        labels={"priority_score": "Priority Score (0–100)", "item_id": "SKU"},
        text="priority_score",
    )
    fig_bar.update_layout(
        plot_bgcolor="#1e2130",
        paper_bgcolor="#1e2130",
        font_color="#e0e0e0",
        yaxis=dict(categoryorder="total ascending"),
        showlegend=True,
        height=420,
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📋 Filtered Action Table</div>', unsafe_allow_html=True)
    st.caption(f"Showing {len(filtered)} SKUs · Filters: Category={sel_cat}, Tier={sel_tier}, Store={sel_store}")

    # Only show items that need reorder by default
    show_all = st.checkbox("Show all SKUs (including no-reorder items)", value=False)
    display_df = filtered if show_all else filtered[filtered["suggested_order_qty_forecast"] > 0]

    # Format the display table
    display_cols = {
        "item_id": "SKU",
        "cat_id": "Category",
        "priority_tier": "Tier",
        "priority_score": "Score",
        "inventory_position": "Inv. Position",
        "forecast_lead_plus_review": "Forecast Demand",
        "safety_stock": "Safety Stock",
        "suggested_order_qty_forecast": "Order Qty",
        "reason_forecast": "Reason",
    }
    available_cols = [c for c in display_cols.keys() if c in display_df.columns]
    table = display_df[available_cols].sort_values("priority_score", ascending=False).copy()
    table = table.rename(columns=display_cols)

    # Color-code the Tier column
    def color_tier(val):
        colors = {"High": "background-color:#C0392B; color:white",
                  "Medium": "background-color:#E67E22; color:white",
                  "Low": "background-color:#27AE60; color:white"}
        return colors.get(val, "")

    def color_score(val):
        if val >= 60:   return "background-color:#C0392B; color:white"
        elif val >= 30: return "background-color:#E67E22; color:white"
        else:           return "background-color:#27AE60; color:white"

    styled = table.style.map(color_tier, subset=["Tier"])
    styled = styled.map(color_score,     subset=["Score"])
    styled = styled.format({"Score": "{:.1f}", "Safety Stock": "{:.1f}",
                             "Forecast Demand": "{:.0f}", "Inv. Position": "{:.0f}"})

    st.dataframe(styled, use_container_width=True, height=400)

    # Download button
    csv_out = table.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Action List CSV", csv_out,
                       file_name="stocksense360_action_list.csv", mime="text/csv")

# ══════════════════════════════════════════════
# TAB 2 — SALES HISTORY + FORECAST
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📈 Sales History + 14-Day Forecast</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2])

    with col_left:
        # SKU selector
        all_skus = sorted(action_df["item_id"].unique().tolist())
        sel_sku = st.selectbox("🔍 Select SKU", all_skus, index=0)

        # Show priority card for selected SKU
        sku_row = action_df[action_df["item_id"] == sel_sku]
        if not sku_row.empty:
            r = sku_row.iloc[0]
            tier = r["priority_tier"]
            badge_class = f"badge-{tier.lower()}"
            st.markdown(f"""
            <div style="background:#1e2130; border:1px solid #2e3250; border-radius:10px; padding:16px; margin-top:12px;">
                <div style="font-size:13px; color:#888;">Priority</div>
                <div style="font-size:22px; font-weight:700; color:#fff;">{r['priority_score']:.1f} / 100
                    &nbsp;<span class="{badge_class}">{tier}</span>
                </div>
                <hr style="border-color:#2e3250; margin:10px 0">
                <div style="font-size:12px; color:#aaa;">📦 On Hand: <b style="color:#fff">{int(r['current_on_hand'])}</b></div>
                <div style="font-size:12px; color:#aaa;">📊 Forecast Demand (14d): <b style="color:#fff">{int(r['forecast_lead_plus_review'])}</b></div>
                <div style="font-size:12px; color:#aaa;">🛡️ Safety Stock: <b style="color:#fff">{r['safety_stock']:.1f}</b></div>
                <div style="font-size:12px; color:#aaa;">🛒 Suggested Order: <b style="color:#e74c3c">{int(r['suggested_order_qty_forecast'])}</b></div>
                <hr style="border-color:#2e3250; margin:10px 0">
                <div style="font-size:11px; color:#7c83ff; font-style:italic;">{r['reason_forecast']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        # Sales history — last 90 days
        ca1_sales = sales_df[(sales_df["store_id"] == "CA_1") & (sales_df["item_id"] == sel_sku)].copy()
        ca1_sales = ca1_sales.sort_values("date")
        hist = ca1_sales.tail(90)

        # Forecast for this SKU
        sku_fore = fore_df[fore_df["item_id"] == sel_sku].copy()

        fig = go.Figure()

        # History line
        fig.add_trace(go.Scatter(
            x=hist["date"], y=hist["units_sold"],
            mode="lines", name="Historical Sales",
            line=dict(color="#7c83ff", width=2),
            fill="tozeroy", fillcolor="rgba(124,131,255,0.1)"
        ))

        # Forecast line
        if not sku_fore.empty:
            fig.add_trace(go.Scatter(
                x=sku_fore["date"], y=sku_fore["forecast_units"],
                mode="lines+markers", name="14-Day Forecast",
                line=dict(color="#e74c3c", width=2, dash="dash"),
                marker=dict(size=6, color="#e74c3c")
            ))

            # Vertical line at forecast start
            split_date = sku_fore["date"].min()
            fig.add_shape(
                type="line",
                x0=split_date, x1=split_date,
                y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="#888888", width=1, dash="dot"),
            )

        fig.update_layout(
            title=f"Sales History (last 90d) + Forecast: {sel_sku}",
            xaxis_title="Date",
            yaxis_title="Units",
            plot_bgcolor="#1e2130",
            paper_bgcolor="#1e2130",
            font_color="#e0e0e0",
            legend=dict(orientation="h", y=1.1),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Category breakdown chart
    st.markdown('<div class="section-header">📦 Units Sold by Category (CA_1 · 2015–2016)</div>', unsafe_allow_html=True)
    ca1_all = sales_df[(sales_df["store_id"] == "CA_1") & (sales_df["date"] >= "2015-01-01")]
    cat_sales = ca1_all.groupby("cat_id")["units_sold"].sum().reset_index()
    fig_cat = px.bar(
        cat_sales, x="cat_id", y="units_sold",
        color="cat_id",
        color_discrete_map={"FOODS": "#7c83ff", "HOUSEHOLD": "#e74c3c", "HOBBIES": "#27AE60"},
        title="Total Units Sold by Category (2015–2016)",
        labels={"units_sold": "Total Units", "cat_id": "Category"},
    )
    fig_cat.update_layout(
        plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
        font_color="#e0e0e0", showlegend=False, height=300
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — FULL DATA EXPLORER
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">📋 Full Action List — All 41 SKUs</div>', unsafe_allow_html=True)
    st.caption("All columns from control_tower_actionlist_CA1.csv")

    show_df = action_df.sort_values("priority_score", ascending=False)
    st.dataframe(show_df, use_container_width=True, height=500)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Priority Score Distribution**")
        fig_hist = px.histogram(
            action_df, x="priority_score", nbins=20,
            color="priority_tier",
            color_discrete_map={"High":"#C0392B","Medium":"#E67E22","Low":"#27AE60"},
        )
        fig_hist.update_layout(plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
                               font_color="#e0e0e0", height=280)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.markdown("**Inventory Position vs Forecast Demand**")
        fig_scatter = px.scatter(
            action_df,
            x="inventory_position",
            y="forecast_lead_plus_review",
            color="priority_tier",
            size="suggested_order_qty_forecast",
            hover_name="item_id",
            color_discrete_map={"High":"#C0392B","Medium":"#E67E22","Low":"#27AE60"},
            labels={"inventory_position": "Inventory Position",
                    "forecast_lead_plus_review": "Forecast Demand (14d)"},
        )
        fig_scatter.add_shape(type="line", x0=0, y0=0,
                              x1=action_df["inventory_position"].max(),
                              y1=action_df["inventory_position"].max(),
                              line=dict(color="#888", dash="dash"))
        fig_scatter.update_layout(plot_bgcolor="#1e2130", paper_bgcolor="#1e2130",
                                  font_color="#e0e0e0", height=280)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("StockSense360 · Built with Streamlit + Plotly · Dataset: Kaggle M5 Forecasting (Walmart-style retail)")
