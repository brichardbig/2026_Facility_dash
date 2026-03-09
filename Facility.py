import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="2026 Performance Dashboard", layout="wide")

st.title("📊 2026 Facility Performance Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
df = pd.read_excel("facility_data_2026.xlsx")

# ---------------------------------------------------
# PREPROCESSING
# ---------------------------------------------------
df['VL_coverage'] = df['VL_coverage'] * 100
df['suppression'] = df['suppression'] * 100

cols_to_round = [
    'Total_tested','Positives','ICT_tested','APN_ict','SNS','Linked',
    'condom_distribution','Newly_diagnosed','TI','Returned',
    'LTFU','TO','Dead','CRPDDP'
]

df[cols_to_round] = df[cols_to_round].astype("Int64")

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------
st.markdown("""
<style>

.metric-card {
    background-color: #f0f4f8;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    text-align: center;
    transition: 0.2s;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

.metric-title {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
}

.metric-delta-positive {
    font-size: 0.9rem;
    color: #16a34a;
}

.metric-delta-negative {
    font-size: 0.9rem;
    color: #dc2626;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# METRIC CARD FUNCTION
# ---------------------------------------------------
def metric_card(title, value, delta=None):

    delta_html = ""

    if delta is not None:
        color_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{color_class}">{arrow} {abs(delta):,}</div>'

    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR FILTER
# ---------------------------------------------------
st.sidebar.header("Filters")

selected_months = st.sidebar.multiselect(
    "Select Months",
    df["Month"].unique(),
    default=df["Month"].unique()
)

filtered_df = df[df["Month"].isin(selected_months)]

# ---------------------------------------------------
# TABS
# ---------------------------------------------------
tab1, tab2 = st.tabs(["🩺 Prevention", "💊 Care & Treatment"])

# ===================================================
# PREVENTION TAB
# ===================================================
with tab1:

    st.subheader("Prevention Metrics")

    total_tested = filtered_df["Total_tested"].sum()
    total_positives = filtered_df["Positives"].sum()
    avg_yield = (total_positives / total_tested * 100) if total_tested > 0 else 0
    total_condoms = filtered_df["condom_distribution"].sum()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        metric_card("Total Tested", f"{total_tested:,}", 1673-total_tested)

    with col2:
        metric_card("Total Positives", f"{total_positives:,}", 53-total_positives)

    with col3:
        metric_card("Average Yield", f"{avg_yield:.1f}%")

    with col4:
        metric_card("Condoms Distributed", f"{total_condoms:,}", 16730-total_condoms)

    # ------------------------------------------------
    # TESTING TREND
    # ------------------------------------------------
    with st.expander("📈 Testing Trends by Month", expanded=True):

        fig1 = px.bar(
            filtered_df,
            x="Month",
            y="Total_tested",
            text="Total_tested",
            title="Total Tested by Month"
        )

        fig1.add_hline(
            y=1673,
            line_dash="dash",
            line_color="red",
            annotation_text="Target (1,673)"
        )

        st.plotly_chart(fig1,use_container_width=True)

    # ------------------------------------------------
    # POSITIVES + YIELD
    # ------------------------------------------------
    with st.expander("Positives & Yield"):

        filtered_df["Yield"] = (
            filtered_df["Positives"] / filtered_df["Total_tested"] * 100
        ).replace([np.inf,-np.inf],0).fillna(0)

        fig2 = go.Figure()

        fig2.add_bar(
            x=filtered_df["Month"],
            y=filtered_df["Positives"],
            name="Positives",
            text=filtered_df["Positives"]
        )

        fig2.add_scatter(
            x=filtered_df["Month"],
            y=filtered_df["Yield"],
            name="Yield %",
            yaxis="y2",
            mode="lines+markers+text",
            text=filtered_df["Yield"].round(1).astype(str)+"%"
        )

        fig2.update_layout(
            yaxis=dict(title="Positives"),
            yaxis2=dict(title="Yield %",overlaying="y",side="right"),
            title="Positives and Yield"
        )

        st.plotly_chart(fig2,use_container_width=True)

    # ------------------------------------------------
    # ICT %
    # ------------------------------------------------
    with st.expander("ICT Testing Percentage"):

        filtered_df["ICT_percentage"] = (
            filtered_df["ICT_tested"] /
            filtered_df["Total_tested"] * 100
        ).replace([np.inf,-np.inf],0)

        fig3 = px.line(
            filtered_df,
            x="Month",
            y="ICT_percentage",
            markers=True,
            title="ICT Percentage"
        )

        st.plotly_chart(fig3,use_container_width=True)

    # ------------------------------------------------
    # ICT TYPES
    # ------------------------------------------------
    with st.expander("ICT Testing Types"):

        df_long = filtered_df.melt(
            id_vars="Month",
            value_vars=["ICT_tested","APN_ict","SNS"],
            var_name="Testing_Type",
            value_name="Count"
        )

        fig4 = px.bar(
            df_long,
            x="Month",
            y="Count",
            color="Testing_Type",
            barmode="group",
            title="ICT Testing Types"
        )

        st.plotly_chart(fig4,use_container_width=True)

# ===================================================
# CARE & TREATMENT TAB
# ===================================================
with tab2:

    st.subheader("Care & Treatment Metrics")

    actual_census = 6712

    net_growth = (
        (filtered_df["Newly_diagnosed"] +
        filtered_df["TI"] +
        filtered_df["Returned"]).sum()
        -
        (filtered_df["LTFU"] +
        filtered_df["TO"] +
        filtered_df["Dead"]).sum()
    )

    total_ltfu = filtered_df["LTFU"].sum()

    total_attrition = (
        filtered_df["LTFU"] +
        filtered_df["TO"] +
        filtered_df["Dead"]
    ).sum()

    ltfu_percent = (
        total_ltfu / total_attrition * 100
        if total_attrition != 0 else 0
    )

    avg_suppression = filtered_df["suppression"].mean()

    col1,col2,col3,col4,col5 = st.columns(5)

    with col1:
        metric_card("Actual Census",f"{actual_census:,}")

    with col2:
        metric_card("Net Growth",f"{net_growth:,}")

    with col3:
        metric_card("LTFU",f"{total_ltfu:,}")

    with col4:
        metric_card("LTFU % Attrition",f"{ltfu_percent:.1f}%")

    with col5:
        metric_card("Viral Suppression",f"{avg_suppression:.1f}%")

    # ------------------------------------------------
    # NET GROWTH CHART
    # ------------------------------------------------
    with st.expander("Net Growth by Month",expanded=True):

        filtered_df["Net_Growth"] = (
            filtered_df["Newly_diagnosed"] +
            filtered_df["TI"] +
            filtered_df["Returned"]
            -
            filtered_df["LTFU"] -
            filtered_df["TO"] -
            filtered_df["Dead"]
        )

        fig6 = px.area(
            filtered_df,
            x="Month",
            y="Net_Growth",
            markers=True,
            title="Net Growth by Month"
        )

        st.plotly_chart(fig6,use_container_width=True)

    # ------------------------------------------------
    # VIRAL SUPPRESSION
    # ------------------------------------------------
    with st.expander("Viral Suppression"):

        fig8 = px.line(
            filtered_df,
            x="Month",
            y="suppression",
            markers=True,
            title="Viral Suppression"
        )

        fig8.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="Target 95%"
        )

        st.plotly_chart(fig8,use_container_width=True)

    # ------------------------------------------------
    # GAUGES
    # ------------------------------------------------
    col_g1,col_g2 = st.columns(2)

    def plot_gauge(title,actual,target,color):

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=actual,
            delta={"reference":target},
            gauge={
                "axis":{"range":[0,target]},
                "bar":{"color":color},
                "threshold":{
                    "line":{"color":"red","width":4},
                    "value":target
                }
            },
            title={"text":title}
        ))

        return fig

    with col_g1:
        st.plotly_chart(
            plot_gauge("Census Progress",6712,7098,"purple"),
            use_container_width=True
        )

    with col_g2:
        st.plotly_chart(
            plot_gauge("CRPDDP Progress",267,700,"green"),
            use_container_width=True
        )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")

st.markdown("""
<div style='text-align:center;color:#6b7280'>
© 2026 Rich Data Analytics – Facility Performance Dashboard
</div>
""", unsafe_allow_html=True)
