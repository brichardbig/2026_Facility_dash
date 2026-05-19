# =========================================================
# 2026 FACILITY PERFORMANCE DASHBOARD
# =========================================================

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="2026 Facility Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

pio.templates.default = "plotly_white"

# =========================================================
# LOAD DATA
# =========================================================
with st.spinner("Loading dashboard..."):
    df = pd.read_excel("facility_data_2026.xlsx")

# =========================================================
# PREPROCESSING
# =========================================================
df['VL_coverage'] = df['VL_coverage'] * 100
df['suppression'] = df['suppression'] * 100

cols_to_round = [
    'Total_tested', 'Positives', 'ICT_tested', 'APN_ict', 'SNS',
    'Linked', 'condom_distribution', 'Newly_diagnosed',
    'TI', 'Returned', 'LTFU', 'TO', 'Dead', 'CRPDDP'
]

df[cols_to_round] = df[cols_to_round].astype('Int64')

# Month ordering
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

df['Month'] = pd.Categorical(
    df['Month'],
    categories=month_order,
    ordered=True
)

df = df.sort_values('Month')

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #f8fafc;
}

/* Hero Header */
.hero {
    background: linear-gradient(90deg, #2563eb, #1e40af);
    padding: 28px;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* Metric Cards */
.metric-card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    border-left: 6px solid #2563eb;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    height: 160px;
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.10);
}

.metric-title {
    color: #64748b;
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 10px;
}

.metric-value {
    color: #0f172a;
    font-size: 34px;
    font-weight: 700;
    line-height: 1.1;
}

.metric-small {
    color: #475569;
    font-size: 14px;
    margin-top: 6px;
}

.metric-positive {
    color: #16a34a;
    font-weight: 700;
}

.metric-negative {
    color: #dc2626;
    font-weight: 700;
}

/* Tabs */
.stTabs [role="tablist"] {
    gap: 12px;
    border-bottom: 2px solid #dbeafe;
}

.stTabs [role="tab"] {
    border-radius: 12px 12px 0 0;
    padding: 10px 24px;
    background-color: #e2e8f0;
    color: #1e3a8a;
    font-weight: 600;
}

.stTabs [role="tab"][aria-selected="true"] {
    background-color: #2563eb;
    color: white;
}

/* Expander */
.stExpander {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    margin-bottom: 18px;
    background: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* Footer */
.custom-footer {
    text-align:center;
    color:#64748b;
    padding:20px;
    font-size:14px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1 style="color:white; margin-bottom:8px;">
        📊 2026 Facility Performance Dashboard
    </h1>

    <p style="color:#dbeafe; font-size:17px; margin:0;">
        Real-time monitoring of Prevention, Care & Treatment indicators
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## 🏥 Facility Dashboard")
st.sidebar.info("Use filters below to explore performance trends.")

selected_months = st.sidebar.multiselect(
    "Select Months",
    options=df['Month'].unique(),
    default=df['Month'].unique()
)

filtered_df = df[df['Month'].isin(selected_months)]

# =========================================================
# METRIC CARD FUNCTION
# =========================================================
def metric_card(title, value, small=None, delta=None):

    delta_html = ""

    if delta is not None:
        delta_class = "metric-positive" if delta >= 0 else "metric-negative"
        delta_html = f'<div class="{delta_class}">{delta:+,}</div>'

    small_html = f'<div class="metric-small">{small}</div>' if small else ""

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {small_html}
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TABS
# =========================================================
tab1, tab2 = st.tabs(["🩺 Prevention", "💊 Care & Treatment"])

# =========================================================
# PREVENTION TAB
# =========================================================
with tab1:

    st.subheader("🧪 Prevention Metrics")

    total_tested = filtered_df['Total_tested'].sum()
    total_positives = filtered_df['Positives'].sum()
    total_ict = filtered_df['ICT_tested'].sum()
    total_condoms = filtered_df['condom_distribution'].sum()
    total_linked = filtered_df['Linked'].sum()

    avg_yield = (total_positives / total_tested * 100) if total_tested else 0
    ict_percent = (total_ict / total_tested * 100) if total_tested else 0
    linkage_percent = (total_linked / total_positives * 100) if total_positives else 0

    testing_target = 1673 * len(filtered_df)
    testing_delta = total_tested - testing_target

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        metric_card("Total Tested", f"{total_tested:,}", delta=testing_delta)

    with col2:
        metric_card("Total Positives", f"{total_positives:,}",
                    f"{avg_yield:.1f}% Yield")

    with col3:
        metric_card("ICT Tested", f"{total_ict:,}",
                    f"{ict_percent:.1f}% of Tested")

    with col4:
        metric_card("Linked to Care", f"{total_linked:,}",
                    f"{linkage_percent:.1f}% Linkage")

    with col5:
        metric_card("Condom Distribution", f"{total_condoms:,}")

    # =====================================================
    # TESTING TRENDS
    # =====================================================
    with st.expander("📈 HIV Testing Trends", expanded=True):

        fig1 = px.bar(
            filtered_df,
            x='Month',
            y='Total_tested',
            text='Total_tested',
            color_discrete_sequence=['#2563eb']
        )

        fig1.update_traces(textposition='outside')

        fig1.add_hline(
            y=1673,
            line_dash="dash",
            line_color="red",
            annotation_text="Target"
        )

        fig1.update_layout(
            height=420,
            title="Monthly HIV Testing",
            yaxis_title="Clients Tested",
            xaxis_title="Month"
        )

        st.plotly_chart(fig1, use_container_width=True)

    # =====================================================
    # POSITIVES & YIELD
    # =====================================================
    with st.expander("🦠 Positives & Yield"):

        filtered_df['Yield'] = (
            filtered_df['Positives'] /
            filtered_df['Total_tested'] * 100
        ).fillna(0)

        fig2 = go.Figure()

        fig2.add_trace(go.Bar(
            x=filtered_df['Month'],
            y=filtered_df['Positives'],
            name="Positives",
            text=filtered_df['Positives']
        ))

        fig2.add_trace(go.Scatter(
            x=filtered_df['Month'],
            y=filtered_df['Yield'],
            name="Yield %",
            yaxis='y2',
            mode='lines+markers+text',
            text=filtered_df['Yield'].round(1).astype(str) + "%",
            textposition='top center',
            line=dict(color="#16a34a", width=3)
        ))

        fig2.update_layout(
            height=420,
            title="Positives & Yield",
            yaxis=dict(title="Positives"),
            yaxis2=dict(
                title="Yield %",
                overlaying='y',
                side='right'
            )
        )

        st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# CARE & TREATMENT
# =========================================================
with tab2:

    st.subheader("💊 Care & Treatment Metrics")

    actual_census = 6854

    net_growth = (
        filtered_df['Newly_diagnosed'] +
        filtered_df['TI'] +
        filtered_df['Returned']
    ).sum() - (
        filtered_df['LTFU'] +
        filtered_df['TO'] +
        filtered_df['Dead']
    ).sum()

    total_ltfu = filtered_df['LTFU'].sum()

    avg_suppression = filtered_df['suppression'].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Actual Census", f"{actual_census:,}")

    with col2:
        metric_card("Net Growth", f"{net_growth:,}")

    with col3:
        metric_card("LTFU", f"{total_ltfu:,}")

    with col4:
        metric_card("Viral Suppression", f"{avg_suppression:.1f}%")

    # =====================================================
    # VIRAL SUPPRESSION
    # =====================================================
    with st.expander("🧬 Viral Coverage & Suppression", expanded=True):

        fig8 = px.line(
            filtered_df,
            x='Month',
            y=['suppression', 'VL_coverage'],
            markers=True,
            color_discrete_map={
                'suppression': '#16a34a',
                'VL_coverage': '#2563eb'
            }
        )

        fig8.update_traces(
            mode='lines+markers+text',
            texttemplate='%{y:.1f}%',
            textposition='top center'
        )

        fig8.add_hline(
            y=95,
            line_dash="dash",
            line_color="red",
            annotation_text="95% Target"
        )

        fig8.update_layout(
            height=450,
            title="Viral Coverage & Suppression",
            yaxis_title="Percentage (%)",
            hovermode="x unified"
        )

        st.plotly_chart(fig8, use_container_width=True)

    # =====================================================
    # GAUGE FUNCTION
    # =====================================================
    def plot_gauge(title, actual, target, color):

        percent = (actual / target) * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",

            value=actual,

            number={
                'font': {
                    'size': 40,
                    'color': color
                }
            },

            title={
                'text': f"<b>{title}</b><br>{percent:.1f}% Achieved",
                'font': {'size': 24}
            },

            gauge={

                'axis': {
                    'range': [0, target],
                    'tickcolor': "#334155"
                },

                'bar': {
                    'color': color,
                    'thickness': 0.4
                },

                'steps': [
                    {'range': [0, target * 0.5], 'color': "#e2e8f0"},
                    {'range': [target * 0.5, target * 0.8], 'color': "#cbd5e1"},
                    {'range': [target * 0.8, target], 'color': "#bbf7d0"}
                ],

                'threshold': {
                    'line': {'color': "red", 'width': 6},
                    'value': target
                }
            }
        ))

        fig.update_layout(
            height=380,
            margin=dict(t=60, b=20, l=20, r=20)
        )

        return fig

    # =====================================================
    # GAUGES
    # =====================================================
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        with st.expander("🎯 Census Progress", expanded=False):

            st.plotly_chart(
                plot_gauge(
                    "Census Progress",
                    actual_census,
                    7098,
                    "#7c3aed"
                ),
                use_container_width=True
            )

    with col_g2:
        with st.expander("🎯 CRPDDP Progress", expanded=False):

            st.plotly_chart(
                plot_gauge(
                    "CRPDDP Progress",
                    298,
                    600,
                    "#16a34a"
                ),
                use_container_width=True
            )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown("""
<div class="custom-footer">
    © 2026 Rich Data Analytics | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
