import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Facility Dashboard", layout="wide")

st.title("Facility Performance Dashboard")

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("data.csv")

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header("Filters")

facilities = st.sidebar.multiselect(
    "Select Facility",
    options=df["Facility"].unique(),
    default=df["Facility"].unique()
)

filtered_df = df[df["Facility"].isin(facilities)]

# ===============================
# METRIC CARD FUNCTION
# ===============================
def metric_card(title, value, delta=None):

    delta_html = ""
    if delta is not None:
        color = "green" if delta >= 0 else "red"
        delta_html = f"<p style='color:{color};font-size:14px'>{delta:+}</p>"

    st.markdown(
        f"""
        <div style="
        background:#f8f9fa;
        padding:20px;
        border-radius:10px;
        text-align:center;
        box-shadow:0 1px 3px rgba(0,0,0,0.1)">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ===============================
# TABS
# ===============================
tab1, tab2 = st.tabs(["Prevention", "Care & Treatment"])

# =====================================================
# PREVENTION
# =====================================================
with tab1:

    st.subheader("Prevention Indicators")

    total_tested = filtered_df["Total_tested"].sum()
    total_positives = filtered_df["Positives"].sum()
    avg_yield = (total_positives / total_tested * 100) if total_tested > 0 else 0
    total_condoms = filtered_df["condom_distribution"].sum()

    total_ict = filtered_df["ICT_tested"].sum()
    ict_percent = (total_ict / total_tested * 100) if total_tested > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Total Tested", f"{total_tested:,}")

    with col2:
        metric_card("Total Positives", f"{total_positives:,}")

    with col3:
        metric_card("Average Yield", f"{avg_yield:.1f}%")

    with col4:
        metric_card("Condoms Distributed", f"{total_condoms:,}")

    with col5:
        metric_card(
            "Total ICT",
            f"{total_ict:,}<br><span style='font-size:14px;color:gray'>({ict_percent:.1f}%)</span>"
        )

    st.divider()

    # ---------------------------
    # TESTING TREND
    # ---------------------------
    st.subheader("Testing Trend")

    monthly_test = filtered_df.groupby("Month")[["Total_tested","Positives"]].sum().reset_index()

    fig = px.line(
        monthly_test,
        x="Month",
        y=["Total_tested","Positives"],
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CARE AND TREATMENT
# =====================================================
with tab2:

    st.subheader("Care & Treatment Indicators")

    total_tx_curr = filtered_df["TX_CURR"].sum()
    total_new = filtered_df["TX_NEW"].sum()
    total_attrition = filtered_df["Attrition"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("TX_CURR", f"{total_tx_curr:,}")

    with col2:
        metric_card("New on ART", f"{total_new:,}")

    with col3:
        metric_card("Total Attrition", f"{total_attrition:,}")

    st.divider()

    # ==========================
    # NET GROWTH
    # ==========================
    st.subheader("Net Growth")

    growth = filtered_df.groupby("Month")[["TX_NEW","Attrition"]].sum().reset_index()
    growth["Net_Growth"] = growth["TX_NEW"] - growth["Attrition"]

    fig = px.area(
        growth,
        x="Month",
        y="Net_Growth"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # ATTRITION
    # ==========================
    st.subheader("Attrition by Month")

    attrition = filtered_df.groupby("Month")[["Deaths","LTFU","Transfers_out"]].sum().reset_index()

    fig = px.bar(
        attrition,
        x="Month",
        y=["Deaths","LTFU","Transfers_out"],
        barmode="group"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # VIRAL SUPPRESSION
    # ==========================
    st.subheader("Viral Suppression")

    vs = filtered_df.groupby("Month")[["VL_tested","VL_suppressed"]].sum().reset_index()
    vs["Suppression_rate"] = (vs["VL_suppressed"] / vs["VL_tested"]) * 100

    fig = px.line(
        vs,
        x="Month",
        y="Suppression_rate",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # GAUGES
    # ==========================

    st.subheader("Progress Indicators")

    col1, col2 = st.columns(2)

    def plot_gauge(title, actual, target, color):

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=actual,
            delta={"reference": target},
            gauge={
                "axis": {"range": [0, target]},
                "bar": {"color": color},
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "value": target
                }
            },
            title={"text": title}
        ))

        fig.update_layout(height=320)

        return fig

    actual_census = total_tx_curr
    actual_crpddp = filtered_df["CRPDDP"].sum()

    with col1:
        st.plotly_chart(
            plot_gauge("Census Progress", actual_census, 7098, "purple"),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            plot_gauge("CRPDDP Progress", actual_crpddp, 700, "green"),
            use_container_width=True
        )
