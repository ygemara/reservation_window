import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Storage King · Lead-to-Lease", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card { background: #f8f9fa; border-radius: 8px; padding: 1rem; text-align: center; }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────

res_movein = pd.DataFrame({
    "days": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18],
    "reservations": [30771,469,231,142,107,67,59,38,27,33,15,18,19,7,4,1,1],
    "label": ["Same day","1d","2d","3d","4d","5d","6d","7d","8d","9d","10d","11d","12d","13d","14d","15d","18d"]
})

cancel_rate = pd.DataFrame({
    "days": list(range(15)) + [15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],
    "label": ["Same day"] + [f"{i}d" for i in range(1,15)] + ["15d","16d","17d","18d","19d","20d","21d","22d","23d","24d","25d","26d","27d","28d","29d"],
    "total": [31849,1015,702,543,431,280,346,172,206,229,120,101,116,215,116,10,12,11,12,12,11,9,5,2,10,4,7,8,7,9],
    "cancelled": [4303,610,419,326,292,189,250,123,141,170,80,78,105,196,108,8,12,8,12,8,11,7,5,1,9,3,5,7,7,9],
    "moved_in": [27546,405,283,217,139,91,96,49,65,59,40,23,11,19,8,2,0,3,0,4,0,2,0,1,1,1,2,1,0,0],
    "cancel_rate": [13.5,60.1,59.7,60.0,67.7,67.5,72.3,71.5,68.4,74.2,66.7,77.2,90.5,91.2,93.1,80,100,72.7,100,66.7,100,77.8,100,50,90,75,71.4,87.5,100,100],
})

reasons = pd.DataFrame({
    "reason": ["Other","Duplicate","Unable to contact","No longer needs","Reservation expired",
               "Stored w/ competitor","No follow-up call","Chose diff. unit","Pricing too high","Stored w/ relative"],
    "cnt": [18595,8652,4277,3772,1322,1164,740,578,443,175],
    "pct": [46.8,21.8,10.8,9.5,3.3,2.9,1.9,1.5,1.1,0.4],
})

sources = pd.DataFrame({
    "source": ["Custom - SK USA","Go Local Interactive","StorageKingUSA.com","AI Agent - Uniti AI",
               "Sparefoot (paid)","Existing Customer","OpenTech Alliance","Call Potential",
               "Referral","Sparefoot.com","storEDGE Rental Ctr","Swivl"],
    "total": [13983,10025,9576,8896,4927,2813,2340,1034,550,281,281,138],
    "moved_in": [5341,6119,6269,892,1281,2138,58,90,410,153,281,6],
    "cancelled": [8308,3901,3242,7471,3509,661,2282,943,136,122,0,124],
    "cancel_rate": [59.4,38.9,33.9,84.0,71.2,23.5,97.5,91.2,24.7,43.4,0.0,89.9],
})

inquiry = pd.DataFrame({
    "type": ["Internet","Walk-in","Phone","Other","Email"],
    "total": [65507,7655,315,75,11],
    "moved_in": [24737,6958,243,63,8],
    "cancelled": [39437,696,72,12,3],
    "cancel_rate": [60.2,9.1,22.9,16.0,27.3],
})

# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("Storage King · Lead-to-Lease Analysis")
st.caption("storedge_prod.fact.leadtoleasedetail · Aug 2025 – May 2026 · 175 sites · 99,603 units")

tab1, tab2 = st.tabs(["📅 Reservation Timing", "❌ Cancellations"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: RESERVATION TIMING
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Same-day cancel rate", "13.5%", delta="Low risk", delta_color="normal")
    col2.metric("Days 1–7 cancel rate", "65.6%", delta="High risk", delta_color="inverse")
    col3.metric("Days 8–14 cancel rate", "79.8%", delta="Very high risk", delta_color="inverse")
    col4.metric("Same-day move-ins", "96.1%", delta="Of all reservations")

    st.markdown("---")

    # ── Chart 1: Reservation → actual move-in ──
    st.subheader("Days: reservation → actual move-in")
    st.caption("Among moved_in tenants · 31,990 records")

    include_sd = st.checkbox("Include same-day", value=True, key="rm_sd")
    rm_data = res_movein if include_sd else res_movein[res_movein["days"] > 0]

    fig2 = go.Figure(go.Bar(
        x=rm_data["label"], y=rm_data["reservations"],
        marker_color=["#378ADD" if d == 0 else "rgba(55,138,221,0.4)" for d in rm_data["days"]],
        marker_line_width=0,
        hovertemplate="%{x}: %{y:,} tenants<extra></extra>"
    ))
    fig2.update_layout(
        height=380, plot_bgcolor="white",
        xaxis=dict(tickangle=45, gridcolor="#f0f0f0"),
        yaxis=dict(type="log", gridcolor="#f0f0f0", title="Count (log)"),
        margin=dict(t=10, b=60, l=50, r=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("96.1% move in the same day they reserve. ~1,200 tenants planned ahead (days 1–18).")
    with st.expander("Show raw data — reservation to move-in"):
        st.dataframe(
            rm_data[["label","reservations"]]
            .rename(columns={"label":"Days","reservations":"Reservations"}),
            use_container_width=True, hide_index=True
        )

    st.markdown("---")

    # ── Chart 2: Cancel rate by reservation lead time ──
    st.subheader("Cancel rate by days between reservation and desired move-in")
    st.caption("Orange line = cancel rate · Blue bars = total reservations (log scale)")

    max_days = st.slider("Max days to show", min_value=7, max_value=29, value=14, step=1)
    show_sameday = st.checkbox("Include same-day (day 0)", value=True)

    cr_filtered = cancel_rate[cancel_rate["days"] <= max_days].copy()
    if not show_sameday:
        cr_filtered = cr_filtered[cr_filtered["days"] > 0]

    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

    fig1.add_trace(go.Bar(
        x=cr_filtered["label"], y=cr_filtered["total"],
        name="Total reservations", marker_color="rgba(181,212,244,0.7)",
        marker_line_color="rgba(133,183,235,0.8)", marker_line_width=1,
        hovertemplate="%{x}<br>Reservations: %{y:,}<extra></extra>"
    ), secondary_y=True)

    fig1.add_trace(go.Scatter(
        x=cr_filtered["label"], y=cr_filtered["cancel_rate"],
        name="Cancel rate %", mode="lines+markers",
        line=dict(color="#D85A30", width=2.5),
        marker=dict(size=7, color="#D85A30"),
        fill="tozeroy", fillcolor="rgba(216,90,48,0.06)",
        hovertemplate="%{x}<br>Cancel rate: %{y:.1f}%<extra></extra>"
    ), secondary_y=False)

    fig1.update_yaxes(title_text="Cancel rate", range=[0, 100],
                      ticksuffix="%", secondary_y=False, gridcolor="#f0f0f0")
    fig1.update_yaxes(title_text="Volume (log)", type="log",
                      secondary_y=True, showgrid=False,
                      tickvals=[100,1000,10000,100000],
                      ticktext=["100","1k","10k","100k"])
    fig1.update_xaxes(tickangle=45, gridcolor="#f0f0f0")
    fig1.update_layout(
        height=420, hovermode="x unified", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.08),
        margin=dict(t=20, b=60, l=60, r=60)
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.info("💡 **Same-day reservations cancel at only 13.5%** — these are high-intent, ready-to-move tenants. The moment someone reserves even 1 day ahead, cancel rate jumps to ~60% and keeps climbing above 90% by day 12.")

    with st.expander("Show raw data — cancel rate by reservation lead time"):
        st.dataframe(
            cr_filtered[["label","total","moved_in","cancelled","cancel_rate"]]
            .rename(columns={"label":"Days","total":"Total","moved_in":"Moved In","cancelled":"Cancelled","cancel_rate":"Cancel Rate %"}),
            use_container_width=True, hide_index=True
        )

    st.markdown("---")

    # ── Chart 3: Desired vs actual move-in ──
    st.subheader("Desired vs actual move-in date")
    st.caption("Green = moved in early · Blue = on time · Orange = moved in late")

    desired_actual = pd.DataFrame({
        "label": ["-9d","-8d","-7d","-6d","-5d","-4d","-3d","-2d","-1d","0","+1d","+2d","+3d","+4d","+5d","+6d","+7d","+8d","+9d","+10d"],
        "n":     [38,22,21,53,49,74,110,145,223,27443,2037,171,111,61,47,35,19,11,6,8],
        "type":  ["early","early","early","early","early","early","early","early","early","on_time","late","late","late","late","late","late","late","late","late","late"]
    })

    color_map = {"early": "#16a34a", "on_time": "#378ADD", "late": "#f0b429"}

    fig_da = go.Figure(go.Bar(
        x=desired_actual["label"],
        y=desired_actual["n"],
        marker_color=[color_map[t] for t in desired_actual["type"]],
        marker_line_width=0,
        hovertemplate="%{x}: %{y:,} tenants<extra></extra>"
    ))
    fig_da.update_layout(
        height=380, plot_bgcolor="white",
        xaxis=dict(tickangle=45, gridcolor="#f0f0f0"),
        yaxis=dict(type="log", gridcolor="#f0f0f0", title="Count (log)"),
        margin=dict(t=10, b=60, l=50, r=20)
    )
    st.plotly_chart(fig_da, use_container_width=True)
    st.success("✅ 89.3% move in exactly on their desired date. Late movers (8.6%) outnumber early movers (2.1%) — people push back, not forward.")

    with st.expander("Show raw data — desired vs actual move-in"):
        st.dataframe(
            desired_actual[["label","n"]].rename(columns={"label":"Days from desired","n":"Tenants"}),
            use_container_width=True, hide_index=True
        )



# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: CANCELLATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Overall cancel rate", "54.7%", delta="39,485 of 72,126 leads", delta_color="inverse")
    col2.metric('"Other" reason', "46.8%", delta="Largest unknown bucket", delta_color="inverse")
    col3.metric("Best source", "23.5%", delta="Existing Customer", delta_color="normal")
    col4.metric("Walk-in cancel rate", "9.1%", delta="vs 60.2% internet", delta_color="normal")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # ── Cancellation reasons ──
    with col_a:
        st.subheader("Cancellation reasons")
        st.caption("Known reasons only · % of total")

        fig4 = go.Figure(go.Bar(
            x=reasons["cnt"],
            y=reasons["reason"],
            orientation="h",
            marker_color=["#e05c3a","#4171d6","#f0b429","#16a34a","#8b5cf6",
                          "#0891b2","#db2777","#65a30d","#d97706","#6b7280"],
            text=[f"{p}%" for p in reasons["pct"]],
            textposition="outside",
            hovertemplate="%{y}: %{x:,} (%{text})<extra></extra>"
        ))
        fig4.update_layout(
            height=380, plot_bgcolor="white",
            xaxis=dict(gridcolor="#f0f0f0", title="Cancellations"),
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=40, l=160, r=60)
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("46.8% logged as 'Other' — no actionable reason captured. Key data quality gap.")

    # ── Cancel rate by inquiry type ──
    with col_b:
        st.subheader("Cancel rate by inquiry type")
        st.caption("Walk-ins convert at 90.9% — internet leads cancel at 60.2%")

        colors_inq = ["#e05c3a" if r > 50 else "#16a34a" if r < 20 else "#f0b429" for r in inquiry["cancel_rate"]]
        fig5 = go.Figure(go.Bar(
            x=inquiry["type"],
            y=inquiry["cancel_rate"],
            marker_color=colors_inq,
            text=[f"{r}%" for r in inquiry["cancel_rate"]],
            textposition="outside",
            hovertemplate="%{x}<br>Cancel rate: %{y:.1f}%<br>Total leads: %{customdata:,}<extra></extra>",
            customdata=inquiry["total"]
        ))
        fig5.update_layout(
            height=380, plot_bgcolor="white",
            yaxis=dict(range=[0,115], ticksuffix="%", gridcolor="#f0f0f0", title="Cancel rate"),
            xaxis=dict(gridcolor="#f0f0f0"),
            margin=dict(t=10, b=40, l=60, r=20)
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.caption("Walk-ins cancel at only 9.1% vs 60.2% for internet leads.")

    st.markdown("---")

    # ── Marketing source table ──
    st.subheader("Cancel rate by marketing source")
    st.caption("Sources with >50 leads · sorted by volume")

    def color_rate(val):
        v = float(val)
        if v >= 80: return "background-color: #fee2e2; color: #991b1b"
        elif v >= 60: return "background-color: #fef3c7; color: #92400e"
        elif v >= 35: return "background-color: #dbeafe; color: #1e40af"
        else: return "background-color: #dcfce7; color: #166534"

    src_display = sources.copy()
    src_display.columns = ["Source","Total","Moved In","Cancelled","Cancel Rate %"]
    src_display["Cancel Rate %"] = src_display["Cancel Rate %"].map("{:.1f}".format)
    src_display["Total"] = src_display["Total"].map("{:,}".format)
    src_display["Moved In"] = src_display["Moved In"].map("{:,}".format)
    src_display["Cancelled"] = src_display["Cancelled"].map("{:,}".format)

    styled = src_display.style.map(color_rate, subset=["Cancel Rate %"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.error("🚨 **Call Center - OpenTech Alliance (97.5%)** and **AI Agent - Uniti AI (84.0%)** together account for 11,236 leads and only 950 move-ins. These channels need immediate review.")
