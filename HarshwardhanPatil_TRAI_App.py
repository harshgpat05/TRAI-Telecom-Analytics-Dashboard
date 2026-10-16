"""
TRAI India Telecom Analytics Dashboard
Author : Harshwardhan Patil
College : Bharati Vidyapeeth College of Engineering, Navi Mumbai
Dataset : TRAI Telecom Analytics Dataset (Jan 2025 – Aug 2026)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TRAI Telecom Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# COLOUR PALETTE
# ──────────────────────────────────────────────────────────
OP_COLORS = {
    "Reliance Jio":            "#2e7d32",
    "Bharti Airtel":           "#e65100",
    "Vodafone Idea":           "#1565c0",
    "BSNL":                    "#880e4f",
    "MTNL":                    "#795548",
    "Reliance Communications": "#607d8b",
}

# ──────────────────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    lsa_raw = pd.read_csv("TRAI_Wireless_LSA_Long.csv", parse_dates=["month"])
    nom = pd.read_excel("TRAI_Telecom_Analytics_Dataset.xlsx",
                        sheet_name="National_Operator_Monthly", parse_dates=["month"])
    ns  = pd.read_excel("TRAI_Telecom_Analytics_Dataset.xlsx",
                        sheet_name="National_Summary", parse_dates=["month"])
    bb  = pd.read_excel("TRAI_Telecom_Analytics_Dataset.xlsx",
                        sheet_name="Broadband_Top5", parse_dates=["month"])

    lsa = lsa_raw[lsa_raw["value_status"] == "reported"].copy()
    lsa["lsa"] = lsa["lsa"].replace({"U.P.(W )": "Uttar Pradesh West"})
    lsa["wireless_mobile_subscribers"] = lsa["wireless_mobile_subscribers"].astype(float)
    lsa["subs_M"] = lsa["wireless_mobile_subscribers"] / 1e6
    lsa = lsa.sort_values(["month","lsa","operator"]).reset_index(drop=True)

    nom["subs_M"] = nom["wireless_mobile_subscribers"] / 1e6
    nom = nom.sort_values(["month","operator"]).reset_index(drop=True)
    ns  = ns.sort_values("month").reset_index(drop=True)
    bb  = bb.sort_values(["month","operator"]).reset_index(drop=True)
    return lsa, nom, ns, bb

lsa, nom, ns, bb = load_data()

MAJOR_OPS  = ["Reliance Jio", "Bharti Airtel", "Vodafone Idea", "BSNL"]
ALL_OPS    = sorted(nom["operator"].unique().tolist())
all_months = sorted(nom["month"].unique())
lsa_months = sorted(lsa["month"].unique())
bb_ops     = sorted(bb["operator"].unique().tolist())
m_labels   = [pd.Timestamp(m).strftime("%b %Y") for m in all_months]
lsa_mlabels= [pd.Timestamp(m).strftime("%B %Y") for m in lsa_months]

# ──────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS (first run only)
# ──────────────────────────────────────────────────────────
def _init(key, val):
    if key not in st.session_state:
        st.session_state[key] = val

_init("ops",           MAJOR_OPS)
_init("m_start_idx",   0)
_init("m_end_idx",     len(all_months) - 1)
_init("lsa_m_idx",     0)
_init("chart_type",    "Line")
_init("metric",        "Subscribers (M)")
_init("bb_ops",        ["Reliance Jio","Bharti Airtel","Vodafone Idea","BSNL"])
_init("bb_metric",     "Broadband Subscribers")
_init("lsa_ops",       MAJOR_OPS)
_init("lsa_view",      "Stacked Bar")
_init("mnp_chart",     "Bar + Trend Line")
_init("dd_metric",     "Subscribers (M)")

# ──────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("https://www.trai.gov.in/sites/default/files/trai_logo_0.png", width=150)
    except Exception:
        st.markdown("## 📡")
    st.markdown("### TRAI Telecom Analytics")
    st.caption("Harshwardhan Patil | Bharati Vidyapeeth COE, Navi Mumbai")
    st.divider()

    page = st.radio("📌 Page", [
        "🏠 Overview",
        "📊 Market Share",
        "📈 Growth Trends",
        "🗺️ LSA Analysis",
        "🌐 Broadband",
        "🔀 MNP & Connectivity",
        "🔍 Operator Deep Dive",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("### 🎛️ Filters")
    st.caption("Changes apply instantly — no submit needed.")

    # ── GLOBAL: Operator selector ──────────────────────────
    st.session_state["ops"] = st.multiselect(
        "📶 Operators",
        options=MAJOR_OPS,
        default=st.session_state["ops"],
        key="_ops_widget",
    )

    # ── GLOBAL: Month range ────────────────────────────────
    r = st.select_slider(
        "📅 Month Range",
        options=list(range(len(all_months))),
        value=(st.session_state["m_start_idx"], st.session_state["m_end_idx"]),
        format_func=lambda i: m_labels[i],
        key="_mrange_widget",
    )
    st.session_state["m_start_idx"] = r[0]
    st.session_state["m_end_idx"]   = r[1]

    # ── PAGE-SPECIFIC filters ──────────────────────────────
    if page == "📊 Market Share":
        st.markdown("**Chart Options**")
        st.session_state["chart_type"] = st.selectbox(
            "📉 Chart Style",
            ["Stacked Area", "Line", "Bar (grouped)", "Pie (latest month)"],
            index=["Stacked Area","Line","Bar (grouped)","Pie (latest month)"].index(
                st.session_state["chart_type"]
            ) if st.session_state["chart_type"] in ["Stacked Area","Line","Bar (grouped)","Pie (latest month)"] else 0,
        )
        st.session_state["metric"] = st.selectbox(
            "📊 Metric",
            ["Market Share (%)", "Subscribers (M)"],
            index=["Market Share (%)","Subscribers (M)"].index(st.session_state["metric"])
            if st.session_state["metric"] in ["Market Share (%)","Subscribers (M)"] else 0,
        )

    elif page == "📈 Growth Trends":
        st.markdown("**Chart Options**")
        st.session_state["chart_type"] = st.selectbox(
            "📉 Chart Style",
            ["Line", "Bar (grouped)", "Area"],
            index=["Line","Bar (grouped)","Area"].index(st.session_state["chart_type"])
            if st.session_state["chart_type"] in ["Line","Bar (grouped)","Area"] else 0,
        )
        st.session_state["metric"] = st.selectbox(
            "📊 Metric",
            ["Subscribers (M)", "MoM Change (M)", "MoM Growth (%)"],
            index=["Subscribers (M)","MoM Change (M)","MoM Growth (%)"].index(st.session_state["metric"])
            if st.session_state["metric"] in ["Subscribers (M)","MoM Change (M)","MoM Growth (%)"] else 0,
        )

    elif page == "🗺️ LSA Analysis":
        st.markdown("**LSA Options**")
        st.session_state["lsa_m_idx"] = st.selectbox(
            "🗓️ Month",
            options=list(range(len(lsa_months))),
            index=st.session_state["lsa_m_idx"],
            format_func=lambda i: lsa_mlabels[i],
        )
        st.session_state["lsa_ops"] = st.multiselect(
            "📶 Operators to show",
            options=MAJOR_OPS,
            default=st.session_state["lsa_ops"],
        )
        st.session_state["lsa_view"] = st.selectbox(
            "📊 Chart Type",
            ["Stacked Bar", "Grouped Bar", "Treemap", "Share % Bar"],
            index=["Stacked Bar","Grouped Bar","Treemap","Share % Bar"].index(
                st.session_state["lsa_view"]
            ) if st.session_state["lsa_view"] in ["Stacked Bar","Grouped Bar","Treemap","Share % Bar"] else 0,
        )

    elif page == "🌐 Broadband":
        st.markdown("**Broadband Options**")
        st.session_state["bb_ops"] = st.multiselect(
            "📶 Operators",
            options=bb_ops,
            default=[o for o in st.session_state["bb_ops"] if o in bb_ops],
        )
        st.session_state["bb_metric"] = st.selectbox(
            "📊 View",
            ["Broadband Subscribers", "Urban vs Rural", "Both"],
            index=["Broadband Subscribers","Urban vs Rural","Both"].index(
                st.session_state["bb_metric"]
            ) if st.session_state["bb_metric"] in ["Broadband Subscribers","Urban vs Rural","Both"] else 0,
        )

    elif page == "🔀 MNP & Connectivity":
        st.markdown("**MNP Options**")
        st.session_state["mnp_chart"] = st.selectbox(
            "📊 Chart Type",
            ["Bar + Trend Line", "Line Only", "Bar Only", "Area"],
            index=["Bar + Trend Line","Line Only","Bar Only","Area"].index(
                st.session_state["mnp_chart"]
            ) if st.session_state["mnp_chart"] in ["Bar + Trend Line","Line Only","Bar Only","Area"] else 0,
        )

    elif page == "🔍 Operator Deep Dive":
        st.markdown("**Deep Dive Options**")
        st.session_state["dd_metric"] = st.selectbox(
            "📊 Primary Metric",
            ["Subscribers (M)", "Market Share (%)", "MoM Change (M)", "MoM Growth (%)"],
            index=["Subscribers (M)","Market Share (%)","MoM Change (M)","MoM Growth (%)"].index(
                st.session_state["dd_metric"]
            ) if st.session_state["dd_metric"] in ["Subscribers (M)","Market Share (%)","MoM Change (M)","MoM Growth (%)"] else 0,
        )

    st.divider()
    if st.button("🔄 Reset All Filters", use_container_width=True):
        for k in ["ops","m_start_idx","m_end_idx","lsa_m_idx","chart_type",
                  "metric","bb_ops","bb_metric","lsa_ops","lsa_view","mnp_chart","dd_metric",
                  "_ops_widget","_mrange_widget"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.caption("Data: TRAI Press Releases 2025–2026")

# ──────────────────────────────────────────────────────────
# RESOLVE ACTIVE FILTER VALUES
# ──────────────────────────────────────────────────────────
ops      = st.session_state["ops"] or MAJOR_OPS
si       = st.session_state["m_start_idx"]
ei       = st.session_state["m_end_idx"]
m_start  = all_months[si]
m_end    = all_months[ei]
sel_mon  = lsa_months[st.session_state["lsa_m_idx"]]

# Filtered national operator data
nom_f = nom[
    nom["operator"].isin(ops) &
    (nom["month"] >= m_start) &
    (nom["month"] <= m_end)
].copy()

def active_banner(extra=""):
    parts = [f"**Operators:** {', '.join(ops)}", f"**Period:** {m_labels[si]} → {m_labels[ei]}"]
    if extra: parts.append(extra)
    st.info("  |  ".join(parts))

def kpi(label, value, delta=None, delta_color="normal"):
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

# ──────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ──────────────────────────────────────────────────────────
if page == "🏠 Overview":
    st.title("🇮🇳 TRAI India Telecom Analytics Dashboard")
    st.markdown("**Wireless Subscriber Trends, Market Share & Broadband Intelligence — Jan 2025 to Aug 2026**")
    st.divider()

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: kpi("📱 Wireless Subs (Aug 2026)", "1,293 M", "+12.3% vs Jan 2025")
    with k2: kpi("📶 Active Wireless (Aug 2026)", "1,208 M", "+11.2% vs Feb 2025")
    with k3: kpi("🌐 Broadband (Aug 2026)", "1,101 M", "+12.4% since Jun 2025")
    with k4: kpi("🥇 Jio Market Share", "39.3%", "-1.2pp vs Jan 2025", "inverse")
    with k5: kpi("🔀 MNP Requests (Aug 2026)", "15.83 M", "+31.3% vs Feb 2025")

    st.divider()
    monthly_total = nom.groupby("month")["subs_M"].sum().reset_index(name="Total_M")
    fig = px.area(monthly_total, x="month", y="Total_M",
                  title="All-India Total Wireless Subscribers (Millions)",
                  labels={"Total_M":"Subscribers (M)","month":"Month"},
                  color_discrete_sequence=["#3b82d4"])
    fig.add_vline(x="2025-08-15", line_dash="dash", line_color="orange",
                  annotation_text="Data Gap →", annotation_position="top left")
    fig.update_traces(fillcolor="rgba(59,130,212,0.12)", line_width=2.5)
    fig.update_layout(hovermode="x unified", height=350)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Operator Snapshot")
        snap = pd.DataFrame({
            "Operator":      ["Reliance Jio","Bharti Airtel","Vodafone Idea","BSNL","MTNL"],
            "Jan 2025 (M)":  [465.8, 387.0, 205.9, 91.6, 1.00],
            "Aug 2026 (M)":  [508.4, 491.6, 199.6, 93.7, 0.155],
            "Change (%)":    ["+9.2%","+27.0%","−3.1%","+2.3%","−84.5%"],
        })
        st.dataframe(snap, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Key National Indicators")
        ind = ns[["month","broadband_total_million","active_wireless_million","mnp_requests_million"]]\
                .dropna(subset=["active_wireless_million"]).sort_values("month").copy()
        ind["month"] = ind["month"].dt.strftime("%b %Y")
        ind.columns = ["Month","Broadband (M)","Active Wireless (M)","MNP (M)"]
        st.dataframe(ind, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# PAGE: MARKET SHARE
# ──────────────────────────────────────────────────────────
elif page == "📊 Market Share":
    st.title("📊 Wireless Market Share Evolution")
    active_banner()
    st.divider()

    k1, k2, k3, k4 = st.columns(4)
    # Dynamic KPIs from filtered data
    if not nom_f.empty:
        latest_f = nom_f[nom_f["month"] == nom_f["month"].max()]
        for col, op in zip([k1,k2,k3,k4], ops[:4]):
            row = latest_f[latest_f["operator"]==op]
            if not row.empty:
                with col:
                    kpi(f"{op.split()[1] if len(op.split())>1 else op}",
                        f"{row['subs_M'].values[0]:.1f}M",
                        f"{row['market_share_pct'].values[0]:.1f}%")
    st.divider()

    metric_col = "market_share_pct" if st.session_state["metric"] == "Market Share (%)" else "subs_M"
    metric_lbl = "Market Share (%)" if metric_col == "market_share_pct" else "Subscribers (M)"
    ctype      = st.session_state["chart_type"]

    if ctype == "Stacked Area":
        ms_piv = nom_f.pivot_table(index="month", columns="operator",
                                    values=metric_col, aggfunc="first").sort_index().reset_index()
        fig = go.Figure()
        for op in ops:
            if op in ms_piv.columns:
                hex_c = OP_COLORS.get(op, "#888")
                r,g,b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
                fig.add_trace(go.Scatter(
                    x=ms_piv["month"], y=ms_piv[op], name=op,
                    stackgroup="one",
                    fillcolor=f"rgba({r},{g},{b},0.75)",
                    line=dict(color=hex_c, width=1), mode="lines"
                ))
        fig.update_layout(title=f"{metric_lbl} — Stacked Area",
                          yaxis_title=metric_lbl, hovermode="x unified", height=420)
        st.plotly_chart(fig, use_container_width=True)

    elif ctype == "Line":
        fig = px.line(nom_f, x="month", y=metric_col, color="operator",
                      color_discrete_map=OP_COLORS, markers=True,
                      title=f"{metric_lbl} — Line Chart",
                      labels={metric_col: metric_lbl, "month":"Month","operator":"Operator"})
        fig.update_layout(hovermode="x unified", height=420)
        st.plotly_chart(fig, use_container_width=True)

    elif ctype == "Bar (grouped)":
        fig = px.bar(nom_f, x="month", y=metric_col, color="operator",
                     color_discrete_map=OP_COLORS, barmode="group",
                     title=f"{metric_lbl} — Grouped Bar",
                     labels={metric_col: metric_lbl, "month":"Month","operator":"Operator"})
        fig.update_layout(hovermode="x unified", height=420)
        st.plotly_chart(fig, use_container_width=True)

    elif ctype == "Pie (latest month)":
        lm = nom_f["month"].max()
        pie_d = nom_f[nom_f["month"]==lm]
        fig = px.pie(pie_d, values=metric_col, names="operator",
                     color="operator", color_discrete_map=OP_COLORS,
                     title=f"{metric_lbl} — {pd.Timestamp(lm).strftime('%B %Y')}",
                     hole=0.38)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("📋 Data Table")
    tbl = nom_f[["month","operator",metric_col]].copy()
    tbl_piv = tbl.pivot_table(index="month", columns="operator",
                               values=metric_col, aggfunc="first").sort_index().reset_index()
    tbl_piv["month"] = tbl_piv["month"].dt.strftime("%b %Y")
    tbl_piv = tbl_piv.round(2)
    st.dataframe(tbl_piv, use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# PAGE: GROWTH TRENDS
# ──────────────────────────────────────────────────────────
elif page == "📈 Growth Trends":
    st.title("📈 Subscriber Growth Trends")
    active_banner()
    st.divider()

    metric  = st.session_state["metric"]
    ctype   = st.session_state["chart_type"]

    metric_map = {
        "Subscribers (M)":    ("subs_M",                      "Subscribers (M)"),
        "MoM Change (M)":     ("month_over_month_change",     "Net Change (M)"),
        "MoM Growth (%)":     ("month_over_month_growth_pct", "Growth (%)"),
    }
    col_key, col_label = metric_map[metric]

    plot_df = nom_f.dropna(subset=[col_key]).copy()
    if col_key == "month_over_month_change":
        plot_df["month_over_month_change"] = plot_df["month_over_month_change"] / 1e6
        col_label = "Net Change (M)"

    if ctype == "Line":
        fig = px.line(plot_df, x="month", y=col_key, color="operator",
                      color_discrete_map=OP_COLORS, markers=True,
                      title=f"{col_label} by Operator — Line Chart",
                      labels={col_key: col_label,"month":"Month","operator":"Operator"})
    elif ctype == "Bar (grouped)":
        fig = px.bar(plot_df, x="month", y=col_key, color="operator",
                     color_discrete_map=OP_COLORS, barmode="group",
                     title=f"{col_label} by Operator — Grouped Bar",
                     labels={col_key: col_label,"month":"Month","operator":"Operator"})
        fig.add_hline(y=0, line_dash="dot", line_color="black", opacity=0.4)
    elif ctype == "Area":
        fig = px.area(plot_df, x="month", y=col_key, color="operator",
                      color_discrete_map=OP_COLORS,
                      title=f"{col_label} by Operator — Area Chart",
                      labels={col_key: col_label,"month":"Month","operator":"Operator"})
    else:
        fig = px.line(plot_df, x="month", y=col_key, color="operator",
                      color_discrete_map=OP_COLORS, markers=True,
                      title=f"{col_label} by Operator",
                      labels={col_key: col_label,"month":"Month","operator":"Operator"})

    fig.update_layout(hovermode="x unified", height=420)
    st.plotly_chart(fig, use_container_width=True)

    # Jio vs Airtel gap (always shown if both selected)
    if "Reliance Jio" in ops and "Bharti Airtel" in ops:
        jio_s    = nom_f[nom_f["operator"]=="Reliance Jio"].set_index("month")["subs_M"]
        airtel_s = nom_f[nom_f["operator"]=="Bharti Airtel"].set_index("month")["subs_M"]
        gap_df   = (jio_s - airtel_s).dropna().reset_index()
        gap_df.columns = ["month","gap_M"]
        if not gap_df.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=gap_df["month"], y=gap_df["gap_M"],
                fill="tozeroy", fillcolor="rgba(124,92,216,0.15)",
                line=dict(color="#7c3aed", width=2.5),
                mode="lines+markers", name="Jio − Airtel Gap"
            ))
            fig2.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5,
                           annotation_text="Parity")
            fig2.update_layout(title="Jio vs Airtel — Subscriber Gap (Millions)",
                               yaxis_title="Gap (M)", hovermode="x unified", height=320)
            st.plotly_chart(fig2, use_container_width=True)

    # Data table
    st.subheader("📋 Data Table")
    tbl = nom_f[["month","operator","subs_M","market_share_pct",
                 "month_over_month_change","month_over_month_growth_pct"]].copy()
    tbl["month"] = tbl["month"].dt.strftime("%b %Y")
    tbl["month_over_month_change"] = (tbl["month_over_month_change"] / 1e6).round(3)
    tbl.columns = ["Month","Operator","Subs (M)","Share (%)","MoM Change (M)","MoM Growth (%)"]
    st.dataframe(tbl.round(2), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# PAGE: LSA ANALYSIS
# ──────────────────────────────────────────────────────────
elif page == "🗺️ LSA Analysis":
    st.title("🗺️ LSA-Level Regional Analysis")
    lsa_ops  = st.session_state["lsa_ops"] or MAJOR_OPS
    lsa_view = st.session_state["lsa_view"]
    active_banner(f"**LSA Month:** {lsa_mlabels[st.session_state['lsa_m_idx']]}")
    st.divider()

    lsa_m = lsa[(lsa["month"] == sel_mon) & (lsa["operator"].isin(lsa_ops))].copy()
    lsa_all = lsa[lsa["month"] == sel_mon].copy()

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Total Subs", f"{lsa_all['subs_M'].sum():.0f} M", "all operators")
    with c2: kpi("LSAs Covered", str(lsa_all["lsa"].nunique()), "")
    with c3:
        top = lsa_all.groupby("lsa")["subs_M"].sum().idxmax()
        kpi("Largest LSA", top, "by subs")
    with c4:
        jn=an=0
        for l in lsa_all["lsa"].unique():
            grp = lsa_all[lsa_all["lsa"]==l]
            leader = grp.sort_values("subs_M",ascending=False).iloc[0]["operator"]
            if leader=="Reliance Jio": jn+=1
            elif leader=="Bharti Airtel": an+=1
        kpi("Jio-Led LSAs", f"{jn}/{lsa_all['lsa'].nunique()}", f"Airtel leads {an}")

    st.divider()

    lsa_totals_m = lsa_m.groupby("lsa")["subs_M"].sum().reset_index(name="total")
    lsa_order    = lsa_totals_m.sort_values("total", ascending=True)["lsa"].tolist()

    if lsa_view == "Stacked Bar":
        lp = lsa_m.merge(lsa_totals_m, on="lsa")
        fig = px.bar(lp, x="subs_M", y="lsa", color="operator",
                     color_discrete_map=OP_COLORS, orientation="h",
                     category_orders={"lsa": lsa_order},
                     title=f"Subscribers per LSA — {lsa_mlabels[st.session_state['lsa_m_idx']]} (Stacked)",
                     labels={"subs_M":"Subscribers (M)","lsa":"LSA","operator":"Operator"})
        fig.update_layout(barmode="stack", hovermode="y unified", height=620)

    elif lsa_view == "Grouped Bar":
        fig = px.bar(lsa_m, x="subs_M", y="lsa", color="operator",
                     color_discrete_map=OP_COLORS, orientation="h",
                     category_orders={"lsa": lsa_order},
                     title=f"Subscribers per LSA — {lsa_mlabels[st.session_state['lsa_m_idx']]} (Grouped)",
                     labels={"subs_M":"Subscribers (M)","lsa":"LSA","operator":"Operator"})
        fig.update_layout(barmode="group", hovermode="y unified", height=700)

    elif lsa_view == "Treemap":
        lsa_m2 = lsa_m[lsa_m["subs_M"] > 0]
        fig = px.treemap(lsa_m2, path=["lsa","operator"], values="subs_M",
                         color="operator", color_discrete_map=OP_COLORS,
                         title=f"Subscriber Treemap — {lsa_mlabels[st.session_state['lsa_m_idx']]}")
        fig.update_layout(height=580)

    elif lsa_view == "Share % Bar":
        lsa_m_s = lsa_m.copy()
        lsa_m_s = lsa_m_s.merge(lsa_totals_m, on="lsa")
        lsa_m_s["share"] = (lsa_m_s["subs_M"] / lsa_m_s["total"] * 100).round(2)
        fig = px.bar(lsa_m_s, x="share", y="lsa", color="operator",
                     color_discrete_map=OP_COLORS, orientation="h",
                     category_orders={"lsa": lsa_order},
                     title=f"Market Share % per LSA — {lsa_mlabels[st.session_state['lsa_m_idx']]}",
                     labels={"share":"Share (%)","lsa":"LSA","operator":"Operator"})
        fig.update_layout(barmode="stack", hovermode="y unified", height=620)
        fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    else:
        fig = go.Figure()

    st.plotly_chart(fig, use_container_width=True)

    # Leader table
    st.subheader("LSA Leader Table")
    rows=[]
    for l in lsa_all["lsa"].unique():
        grp = lsa_all[lsa_all["lsa"]==l].sort_values("subs_M",ascending=False)
        tot = grp["subs_M"].sum()
        lr  = grp.iloc[0]
        rows.append({"LSA":l, "Total (M)":round(tot,2),
                     "Leader":lr["operator"],
                     "Leader Subs (M)":round(lr["subs_M"],2),
                     "Leader Share (%)":round(lr["subs_M"]/tot*100,1) if tot>0 else 0})
    st.dataframe(pd.DataFrame(rows).sort_values("Total (M)",ascending=False),
                 use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# PAGE: BROADBAND
# ──────────────────────────────────────────────────────────
elif page == "🌐 Broadband":
    st.title("🌐 Broadband Subscriber Analysis")
    bb_ops_sel = st.session_state["bb_ops"]
    bb_view    = st.session_state["bb_metric"]
    active_banner(f"**Broadband View:** {bb_view}")
    st.divider()

    k1,k2,k3,k4 = st.columns(4)
    with k1: kpi("Broadband Total (Aug 2026)","1,101 M","+121.5M in 14 months")
    with k2: kpi("Jio BB Share","~51%","Consistent leader")
    with k3: kpi("Airtel BB Growth","+74%","289M → ~505M")
    with k4: kpi("Rural Telephone (Aug 2026)","558.4 M","+20.6M vs Aug 2025")
    st.divider()

    bb_filtered = bb[bb["operator"].isin(bb_ops_sel)].copy() if bb_ops_sel else bb.copy()
    ns_bb = ns.dropna(subset=["broadband_total_million"]).sort_values("month")
    ns_ur = ns.dropna(subset=["urban_telephone_total_million","rural_telephone_total_million"]).sort_values("month")

    if bb_view in ["Broadband Subscribers","Both"]:
        col1,col2 = st.columns(2)
        with col1:
            fig = px.line(bb_filtered, x="month", y="broadband_subscribers_million",
                          color="operator", color_discrete_map=OP_COLORS, markers=True,
                          title="Broadband Subscribers by Operator (Millions)",
                          labels={"broadband_subscribers_million":"Broadband (M)",
                                  "month":"Month","operator":"Operator"})
            fig.update_layout(hovermode="x unified", height=380)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=ns_bb["month"], y=ns_bb["broadband_total_million"],
                                      mode="lines+markers", fill="tozeroy",
                                      fillcolor="rgba(124,92,216,0.12)",
                                      line=dict(color="#7c3aed",width=2.5),
                                      name="National Total"))
            fig2.update_layout(title="National Broadband Total (Millions)",
                               yaxis_title="Subscribers (M)", hovermode="x unified", height=380)
            st.plotly_chart(fig2, use_container_width=True)

    if bb_view in ["Urban vs Rural","Both"]:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ns_ur["month"], y=ns_ur["urban_telephone_total_million"],
                                  name="Urban", line=dict(color="#1a3a5c",width=2.5),
                                  mode="lines+markers", fill="tozeroy",
                                  fillcolor="rgba(26,58,92,0.07)"))
        fig3.add_trace(go.Scatter(x=ns_ur["month"], y=ns_ur["rural_telephone_total_million"],
                                  name="Rural", line=dict(color="#16a34a",width=2.5),
                                  mode="lines+markers", fill="tozeroy",
                                  fillcolor="rgba(22,163,74,0.07)"))
        fig3.update_layout(title="Urban vs Rural Telephone Subscribers (Millions)",
                           yaxis_title="Subscribers (M)", hovermode="x unified", height=380)
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📋 Broadband Data Table")
    bb_piv = bb_filtered.pivot_table(
        index="month", columns="operator",
        values="broadband_subscribers_million", aggfunc="first"
    ).sort_index().reset_index()
    bb_piv["month"] = bb_piv["month"].dt.strftime("%b %Y")
    st.dataframe(bb_piv.round(2), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# PAGE: MNP & CONNECTIVITY
# ──────────────────────────────────────────────────────────
elif page == "🔀 MNP & Connectivity":
    st.title("🔀 MNP & Connectivity Metrics")
    mnp_ctype = st.session_state["mnp_chart"]
    active_banner(f"**MNP Chart:** {mnp_ctype}")
    st.divider()

    k1,k2,k3,k4 = st.columns(4)
    with k1: kpi("MNP (Aug 2026)","15.83 M","Highest recorded")
    with k2: kpi("MNP Growth","  +31.3%","Feb 2025 → Aug 2026")
    with k3: kpi("Lowest MNP","Feb 2025","12.06 M")
    with k4: kpi("Total Telephone (Aug 2026)","1,361 M","+11.7% vs Jun 2025")
    st.divider()

    ns_mnp = ns.dropna(subset=["mnp_requests_million"]).sort_values("month").copy()
    col1,col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        if mnp_ctype in ["Bar + Trend Line","Bar Only"]:
            fig.add_trace(go.Bar(x=ns_mnp["month"], y=ns_mnp["mnp_requests_million"],
                                 marker_color="#d97706", name="MNP Requests",
                                 text=ns_mnp["mnp_requests_million"].round(2),
                                 textposition="outside"))
        if mnp_ctype in ["Bar + Trend Line","Line Only"]:
            fig.add_trace(go.Scatter(x=ns_mnp["month"], y=ns_mnp["mnp_requests_million"],
                                     mode="lines+markers", line=dict(color="#92400e",width=2.5),
                                     name="Trend"))
        if mnp_ctype == "Area":
            fig.add_trace(go.Scatter(x=ns_mnp["month"], y=ns_mnp["mnp_requests_million"],
                                     mode="lines", fill="tozeroy",
                                     fillcolor="rgba(217,119,6,0.2)",
                                     line=dict(color="#d97706",width=2.5),
                                     name="MNP"))
        fig.update_layout(title="Monthly MNP Requests (Millions)",
                          yaxis_title="MNP Requests (M)", height=380, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tbl = ns_mnp.copy()
        tbl["vs Feb 2025"] = ((tbl["mnp_requests_million"] / 12.06 - 1)*100).round(1).astype(str)+"%"
        tbl["month"] = tbl["month"].dt.strftime("%b %Y")
        tbl = tbl[["month","mnp_requests_million","vs Feb 2025"]]
        tbl.columns = ["Month","MNP (M)","vs Feb 2025"]
        st.subheader("MNP Data Table")
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        ns_aw = ns.dropna(subset=["active_wireless_million"]).sort_values("month")
        fig2 = px.line(ns_aw, x="month", y="active_wireless_million",
                       title="Active Wireless Subscribers (M)",
                       labels={"active_wireless_million":"Active (M)","month":"Month"},
                       markers=True, color_discrete_sequence=["#3b82d4"])
        fig2.update_layout(height=260)
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("🧠 Competitive Intelligence")
    ci1,ci2,ci3 = st.columns(3)
    with ci1:
        st.info("📶 **3-Player Oligopoly** — Jio+Airtel+Vi = 99.97% of all wireless subs.")
        st.success("🏙️ **Urban Boom** — Urban grew +18.1% vs rural +3.7% (Aug 2025–Aug 2026).")
    with ci2:
        st.warning("🔄 **Rising Churn** — 15.83M MNP requests/month is a new record high.")
        st.error("📉 **Rural Divide** — Rural share fell 44.2% → 41.0% in one year.")
    with ci3:
        st.success("🚀 **5G Push** — Airtel's 5G rollout drove +104M subs gain.")
        st.info("📊 **BB Crossover** — India crossed 1 billion broadband subscribers.")

# ──────────────────────────────────────────────────────────
# PAGE: OPERATOR DEEP DIVE
# ──────────────────────────────────────────────────────────
elif page == "🔍 Operator Deep Dive":
    st.title("🔍 Operator Deep Dive")
    dd_metric = st.session_state["dd_metric"]
    active_banner(f"**Metric:** {dd_metric}")
    st.divider()

    if not ops:
        st.warning("Select at least one operator in the sidebar.")
        st.stop()

    metric_map = {
        "Subscribers (M)":   ("subs_M",                      "Subscribers (M)"),
        "Market Share (%)":  ("market_share_pct",             "Market Share (%)"),
        "MoM Change (M)":    ("month_over_month_change",      "MoM Change (M)"),
        "MoM Growth (%)":    ("month_over_month_growth_pct",  "MoM Growth (%)"),
    }
    col_key, col_lbl = metric_map[dd_metric]
    plot_df = nom_f.dropna(subset=[col_key]).copy()
    if col_key == "month_over_month_change":
        plot_df["month_over_month_change"] = plot_df["month_over_month_change"] / 1e6

    # Main chart
    fig = px.line(plot_df, x="month", y=col_key, color="operator",
                  color_discrete_map=OP_COLORS, markers=True,
                  title=f"{col_lbl} — Selected Operators",
                  labels={col_key: col_lbl, "month":"Month","operator":"Operator"})
    fig.update_layout(hovermode="x unified", height=420)
    st.plotly_chart(fig, use_container_width=True)

    # Secondary charts
    col1,col2 = st.columns(2)
    with col1:
        fig2 = px.bar(plot_df, x="month", y=col_key, color="operator",
                      color_discrete_map=OP_COLORS, barmode="group",
                      title=f"{col_lbl} — Grouped Bar",
                      labels={col_key: col_lbl,"month":"Month","operator":"Operator"})
        fig2.add_hline(y=0, line_dash="dot", line_color="black", opacity=0.4)
        fig2.update_layout(hovermode="x unified", height=360)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Pie for latest filtered month
        lm = nom_f["month"].max()
        pie_d = nom_f[nom_f["month"]==lm].dropna(subset=[col_key])
        if not pie_d.empty:
            fig3 = px.pie(pie_d, values=col_key, names="operator",
                          color="operator", color_discrete_map=OP_COLORS,
                          title=f"{col_lbl} Pie — {pd.Timestamp(lm).strftime('%B %Y')}",
                          hole=0.38)
            fig3.update_traces(textposition="inside", textinfo="percent+label")
            fig3.update_layout(height=360)
            st.plotly_chart(fig3, use_container_width=True)

    # Summary statistics table
    st.subheader("📋 Summary Statistics")
    rows=[]
    for op in ops:
        d = nom_f[nom_f["operator"]==op].sort_values("month")
        if len(d) < 1: continue
        v0  = d.iloc[0]["subs_M"]; v1 = d.iloc[-1]["subs_M"]
        ms0 = d.iloc[0]["market_share_pct"]; ms1 = d.iloc[-1]["market_share_pct"]
        rows.append({
            "Operator":        op,
            "From":            d.iloc[0]["month"].strftime("%b %Y"),
            "Subs Start (M)":  round(v0,1),
            "To":              d.iloc[-1]["month"].strftime("%b %Y"),
            "Subs End (M)":    round(v1,1),
            "Net Change (M)":  round(v1-v0,1),
            "Growth (%)":      f"{(v1/v0-1)*100:+.1f}%" if v0>0 else "N/A",
            "Share Δ (pp)":    f"{ms1-ms0:+.2f}",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Full raw data table
    st.subheader("📄 Full Filtered Data")
    raw = nom_f[["month","operator","subs_M","market_share_pct",
                 "month_over_month_change","month_over_month_growth_pct"]].copy()
    raw["month"] = raw["month"].dt.strftime("%b %Y")
    raw["month_over_month_change"] = (raw["month_over_month_change"]/1e6).round(3)
    raw.columns = ["Month","Operator","Subs (M)","Share (%)","MoM Δ (M)","MoM Δ (%)"]
    st.dataframe(raw.round(2), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────
st.divider()
st.caption(
    "📡 TRAI India Telecom Analytics Dashboard  |  "
    "Author: **Harshwardhan Patil**  |  "
    "Bharati Vidyapeeth College of Engineering, Navi Mumbai  |  "
    "Data: TRAI Press Releases 2025–2026"
)
