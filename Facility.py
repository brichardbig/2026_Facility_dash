import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------- Page Setup ----------------------------
st.set_page_config(page_title="2026 Performance Dashboard", layout="wide")
st.title("📊 2026 Facility Performance Dashboard")

# ---------------------------- Load Data ----------------------------
df = pd.read_excel('facility_data_2026.xlsx')

# ---------------------------- Preprocessing ----------------------------
df['VL_coverage'] = df['VL_coverage'] * 100
df['suppression'] = df['suppression'] * 100

cols_to_round = [
    'Total_tested', 'Positives', 'ICT_tested', 'APN_ict', 'SNS', 'Linked',
    'condom_distribution', 'Newly_diagnosed', 'TI', 'Returned',
    'LTFU', 'TO', 'Dead', 'CRPDDP'
]
df[cols_to_round] = df[cols_to_round].astype('Int64')

# ---------------------------- AHF Brand Colors ----------------------------
# Primary: AHF Red     #CC0000
# Dark:    AHF Black   #1A1A1A
# Light:   AHF White   #FFFFFF
# Accent:  Light Red   #FF4D4D
# Muted:   Light Grey  #F5F5F5
# Text:    Dark Grey   #333333

AHF_RED       = "#CC0000"
AHF_DARK_RED  = "#990000"
AHF_BLACK     = "#1A1A1A"
AHF_WHITE     = "#FFFFFF"
AHF_LIGHT_RED = "#FF4D4D"
AHF_GREY_BG   = "#F5F5F5"
AHF_GREY_TEXT = "#333333"
AHF_MID_GREY  = "#888888"

# Chart color sequences based on AHF palette
AHF_CHART_COLORS = [AHF_RED, AHF_BLACK, "#FF6666", "#4D4D4D", "#FF9999", "#808080"]

# ---------------------------- Custom CSS ----------------------------
st.markdown(f"""
<style>
/* ---- Global Background ---- */
.stApp {{
    background-color: {AHF_GREY_BG};
}}

/* ---- Title ---- */
h1 {{
    color: {AHF_RED} !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}}
h2 {{
    color: {AHF_BLACK} !important;
    border-left: 5px solid {AHF_RED};
    padding-left: 10px;
}}

/* ---- Metric Cards ---- */
.metric-card {{
    background: linear-gradient(135deg, {AHF_RED}, {AHF_DARK_RED});
    padding: 20px 16px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(204,0,0,0.25);
    text-align: center;
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(204,0,0,0.35);
}}
.metric-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: rgba(255,255,255,0.85);
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.metric-value {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {AHF_WHITE};
    line-height: 1.2;
}}
.metric-value small, .metric-value span {{
    font-size: 0.82rem;
    color: rgba(255,255,255,0.75);
    font-weight: 400;
}}
.metric-delta-positive {{
    color: #90EE90;
    font-weight: 600;
    margin-top: 6px;
    font-size: 0.85rem;
}}
.metric-delta-negative {{
    color: #FFB3B3;
    font-weight: 600;
    margin-top: 6px;
    font-size: 0.85rem;
}}

/* ---- Tabs ---- */
.stTabs {{ margin-bottom: 20px; }}
.stTabs [role="tablist"] {{
    border-bottom: 3px solid {AHF_RED};
    display: flex;
    gap: 6px;
}}
.stTabs [role="tab"] {{
    padding: 8px 22px;
    border-radius: 10px 10px 0 0;
    background-color: #e8e8e8;
    color: {AHF_BLACK};
    font-weight: 600;
    font-size: 1rem;
    transition: background 0.3s, transform 0.2s;
}}
.stTabs [role="tab"]:hover {{
    background-color: #FFE0E0;
    color: {AHF_RED};
    transform: translateY(-2px);
}}
.stTabs [role="tab"][aria-selected="true"] {{
    background-color: {AHF_RED};
    color: {AHF_WHITE};
    border-bottom: 3px solid {AHF_RED};
    box-shadow: 0 4px 12px rgba(204,0,0,0.3);
}}

/* ---- Expander ---- */
.stExpander > div:first-child {{
    background-color: {AHF_WHITE};
    border-left: 4px solid {AHF_RED};
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}
.stExpander > div:first-child:hover {{
    background-color: #FFF5F5;
}}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {{
    background-color: {AHF_BLACK} !important;
}}
[data-testid="stSidebar"] * {{
    color: {AHF_WHITE} !important;
}}
[data-testid="stSidebar"] .stMultiSelect > div {{
    background-color: #2a2a2a !important;
    border-color: {AHF_RED} !important;
}}

/* ---- Footer ---- */
footer {{ visibility: hidden; }}
.custom-footer {{
    text-align: center;
    color: {AHF_MID_GREY};
    font-size: 0.85rem;
    margin-top: 40px;
    padding: 20px 0;
    border-top: 2px solid {AHF_RED};
}}
.ahf-logo-text {{
    color: {AHF_RED};
    font-weight: 800;
    font-size: 1.1rem;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------- Metric Card Function ----------------------------
def metric_card(title, value, delta=None):
    delta_html = ""
    if delta is not None:
        color_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{color_class}">{arrow} {delta:+,}</div>'
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------- Gauge Chart Function ----------------------------
def plot_gauge(title, actual, target, color=AHF_RED):
    pct = round((actual / target) * 100, 1)
    remaining = max(target - actual, 0)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=actual,
        number={
            'font': {'size': 38, 'color': color},
            'valueformat': ','
        },
        title={
            'text': f"<b>{title}</b><br><span style='font-size:15px;color:{AHF_MID_GREY}'>{pct}% Achieved</span>",
            'font': {'size': 20, 'color': AHF_BLACK}
        },
        gauge={
            'axis': {
                'range': [0, target],
                'tickwidth': 1,
                'tickcolor': "#d1d5db",
                'tickfont': {'size': 11, 'color': AHF_MID_GREY},
                'nticks': 5
            },
            'bar': {'color': color, 'thickness': 0.35},
            'bgcolor': AHF_WHITE,
            'borderwidth': 0,
            'steps': [
                {'range': [0, target * 0.5],  'color': "#f5f5f5"},
                {'range': [target * 0.5, target * 0.8], 'color': "#ffe0e0"},
                {'range': [target * 0.8, target], 'color': "#ffb3b3"}
            ],
            'threshold': {
                'line': {'color': AHF_DARK_RED, 'width': 3},
                'thickness': 0.75,
                'value': target
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(t=80, b=30, l=30, r=30),
        paper_bgcolor=AHF_WHITE,
        font={'family': "Arial"}
    )
    return fig, pct, remaining

# ---------------------------- Chart Layout Helper ----------------------------
def ahf_layout(fig, title="", xaxis_title="", yaxis_title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color=AHF_BLACK, size=16, family="Arial")),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        paper_bgcolor=AHF_WHITE,
        plot_bgcolor="#FAFAFA",
        font=dict(family="Arial", color=AHF_GREY_TEXT),
        xaxis=dict(gridcolor="#EEEEEE", linecolor="#CCCCCC"),
        yaxis=dict(gridcolor="#EEEEEE", linecolor="#CCCCCC"),
    )
    return fig

# ---------------------------- Sidebar Filter ----------------------------
st.sidebar.markdown(f"<div style='text-align:center;padding:10px 0 20px'>"
                    f"<span class='ahf-logo-text'>⚕ AHF Dashboard</span></div>",
                    unsafe_allow_html=True)
st.sidebar.header("Filters")
selected_months = st.sidebar.multiselect(
    "Select Months",
    options=df['Month'].unique(),
    default=df['Month'].unique()
)
filtered_df = df[df['Month'].isin(selected_months)]

# ---------------------------- Tabs ----------------------------
tab1, tab2 = st.tabs(["🩺 Prevention", "💊 Care & Treatment"])

# ==================================================
# PREVENTION TAB
# ==================================================
with tab1:
    st.header("Prevention Metrics")

    total_tested    = filtered_df['Total_tested'].sum()
    total_positives = filtered_df['Positives'].sum()
    avg_yield       = (total_positives / total_tested * 100) if total_tested > 0 else 0
    total_ict       = filtered_df['ICT_tested'].sum()
    ict_percent     = (total_ict / total_tested * 100) if total_tested > 0 else 0
    total_condoms   = filtered_df['condom_distribution'].sum()
    total_linked    = filtered_df['Linked'].sum()
    linkage_percent = (total_linked / total_positives * 100) if total_positives > 0 else 0
    testing_target  = 1673 * len(filtered_df)
    testing_delta   = int(total_tested - testing_target)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Tested", f"{total_tested:,}", testing_delta)
    with col2:
        metric_card("Total Positives", f"{total_positives:,}<br><small>({avg_yield:.1f}% yield)</small>")
    with col3:
        metric_card("Total ICT", f"{total_ict:,}<br><small>({ict_percent:.1f}% of tested)</small>")
    with col4:
        metric_card("Linkage to Care", f"{total_linked:,}<br><small>({linkage_percent:.1f}%)</small>")
    with col5:
        metric_card("Condoms Distributed", f"{total_condoms:,}")

    # Testing Trends
    with st.expander("📈 HIV Testing Trends by Month", expanded=True):
        fig1 = px.bar(
            filtered_df, x='Month', y='Total_tested', text='Total_tested',
            title="HIV Testing Trends by Month",
            color_discrete_sequence=[AHF_RED]
        )
        fig1.update_traces(textposition='outside', marker_line_color=AHF_DARK_RED, marker_line_width=1)
        fig1.add_hline(y=1673, line_dash="dash", line_color=AHF_BLACK, line_width=2,
                       annotation_text="Target = 1,673", annotation_position="top left",
                       annotation_font_color=AHF_BLACK)
        ahf_layout(fig1, yaxis_title="Number Tested", xaxis_title="Month")
        st.plotly_chart(fig1, use_container_width=True)

    # Positives & Yield
    with st.expander("Positives & Yield"):
        filtered_df['Yield'] = (filtered_df['Positives'] / filtered_df['Total_tested'] * 100)\
                               .replace([np.inf, -np.inf], 0).fillna(0)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=filtered_df['Month'], y=filtered_df['Positives'], name="Positives",
            text=filtered_df['Positives'], textposition='outside',
            marker_color=AHF_RED, marker_line_color=AHF_DARK_RED, marker_line_width=1
        ))
        fig2.add_trace(go.Scatter(
            x=filtered_df['Month'], y=filtered_df['Yield'], name="Yield (%)",
            yaxis='y2', mode='lines+markers+text',
            text=filtered_df['Yield'].round(1).astype(str) + "%",
            textposition='top center',
            line=dict(color=AHF_BLACK, width=2),
            marker=dict(color=AHF_BLACK, size=8)
        ))
        fig2.update_layout(
            yaxis=dict(title="Positives", gridcolor="#EEEEEE"),
            yaxis2=dict(title="Yield (%)", overlaying='y', side='right'),
            title="Positives and Yield by Month",
            paper_bgcolor=AHF_WHITE, plot_bgcolor="#FAFAFA",
            font=dict(family="Arial", color=AHF_GREY_TEXT)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ICT %
    with st.expander("ICT - HTS Percentage"):
        filtered_df['ICT_percentage'] = (
            filtered_df['ICT_tested'] / filtered_df['Total_tested'] * 100
        ).replace([np.inf, -np.inf], 0).fillna(0)
        fig3 = px.line(
            filtered_df, x='Month', y='ICT_percentage', markers=True,
            text=filtered_df['ICT_percentage'].round(1).astype(str) + "%",
            title="ICT Testing Percentage by Month",
            color_discrete_sequence=[AHF_RED]
        )
        fig3.update_traces(textposition='top center', line=dict(width=2.5),
                           marker=dict(size=9, color=AHF_RED))
        fig3.add_hline(y=30, line_dash="dash", line_color=AHF_BLACK, line_width=2,
                       annotation_text="Target = 30%", annotation_position="top left",
                       annotation_font_color=AHF_BLACK)
        ahf_layout(fig3, yaxis_title="ICT Percentage (%)", xaxis_title="Month")
        fig3.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig3, use_container_width=True)

    # ICT Testing Types
    with st.expander("ICT Testing Types"):
        df_long = filtered_df.melt(
            id_vars='Month',
            value_vars=['ICT_tested', 'APN_ict', 'SNS'],
            var_name='Testing_Type', value_name='Count'
        )
        fig4 = px.bar(
            df_long, x='Month', y='Count', color='Testing_Type',
            barmode='group', text='Count',
            title="ICT Testing Types",
            color_discrete_map={
                'ICT_tested': AHF_RED,
                'APN_ict':    AHF_BLACK,
                'SNS':        "#FF6666"
            }
        )
        fig4.update_traces(textposition='outside')
        fig4.add_hline(y=502, line_dash="dash", line_color=AHF_DARK_RED, line_width=2,
                       annotation_text="Target = 502", annotation_position="top left",
                       annotation_font_color=AHF_DARK_RED)
        ahf_layout(fig4, yaxis_title="Number Tested", xaxis_title="Month")
        st.plotly_chart(fig4, use_container_width=True)

    # Linkage
    with st.expander("Linkage to Care (%)"):
        filtered_df['Linkage'] = (filtered_df['Linked'] / filtered_df['Positives'] * 100)
        fig5 = px.line(
            filtered_df, x='Month', y='Linkage', markers=True,
            text=filtered_df['Linkage'].round(1).astype(str) + "%",
            title="Linkage to Care (%)",
            color_discrete_sequence=[AHF_RED]
        )
        fig5.update_traces(textposition='top center', line=dict(width=2.5),
                           marker=dict(size=9))
        ahf_layout(fig5, yaxis_title="Linkage (%)", xaxis_title="Month")
        st.plotly_chart(fig5, use_container_width=True)

    # Condom Table
    with st.expander("🧷 Condom Distribution by Month"):
        condom_table = filtered_df[['Month', 'condom_distribution']].copy()
        condom_table['Target'] = 16730
        condom_table['% Achieved'] = (condom_table['condom_distribution'] / 16730) * 100
        st.dataframe(condom_table, use_container_width=True)

# ==================================================
# CARE & TREATMENT TAB
# ==================================================
with tab2:
    st.header("Care and Treatment Metrics")

    actual_census  = 6854
    net_growth     = (
        filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']
    ).sum() - (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']).sum()
    total_ltfu     = filtered_df['LTFU'].sum()
    total_attrition = (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']).sum()
    ltfu_percent   = (total_ltfu / total_attrition * 100) if total_attrition != 0 else 0
    avg_suppression = filtered_df['suppression'].mean()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Actual Census", f"{actual_census:,}")
    with col2:
        metric_card("Net Growth", f"{net_growth:,}")
    with col3:
        metric_card("LTFU", f"{total_ltfu:,}")
    with col4:
        metric_card("LTFU % of Attrition", f"{ltfu_percent:.1f}%")
    with col5:
        metric_card("Viral Suppression (%)", f"{avg_suppression:.1f}%")

    filtered_df['Net_Growth'] = (
        filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']
    ) - (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead'])

    # Net Growth Table
    with st.expander("Net Growth Table", expanded=False):
        net_growth_table = filtered_df[[
            'Month', 'Newly_diagnosed', 'TI', 'Returned',
            'LTFU', 'TO', 'Dead', 'Net_Growth'
        ]].copy()
        net_growth_table['Target'] = 45
        st.dataframe(net_growth_table, use_container_width=True)

    # Net Growth Chart
    with st.expander("Net Growth by Month", expanded=True):
        fig6 = px.area(
            filtered_df, x='Month', y='Net_Growth', markers=True,
            text=filtered_df['Net_Growth'],
            title="Net Growth by Month",
            color_discrete_sequence=[AHF_RED]
        )
        fig6.update_traces(
            textposition='top center',
            line=dict(color=AHF_DARK_RED, width=2.5),
            fillcolor="rgba(204,0,0,0.15)"
        )
        ahf_layout(fig6, yaxis_title="Net Growth", xaxis_title="Month")
        st.plotly_chart(fig6, use_container_width=True)

    # Attrition
    with st.expander("Attrition by Month"):
        filtered_df['Total_Attrition'] = filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']
        fig7 = px.bar(
            filtered_df, x='Month',
            y=['LTFU', 'TO', 'Dead', 'Total_Attrition'],
            barmode='group', text_auto=True,
            title="Attrition by Month",
            color_discrete_map={
                'LTFU':           AHF_RED,
                'TO':             AHF_BLACK,
                'Dead':           "#FF6666",
                'Total_Attrition': "#808080"
            }
        )
        fig7.update_traces(textposition='outside')
        ahf_layout(fig7, yaxis_title="Count", xaxis_title="Month")
        st.plotly_chart(fig7, use_container_width=True)

    # Viral Coverage and Suppression
    with st.expander("Viral Coverage and Suppression by Month"):
        fig8 = px.line(
            filtered_df, x='Month',
            y=['suppression', 'VL_coverage'],
            markers=True,
            title="Viral Coverage and Suppression by Month",
            color_discrete_map={
                'suppression': AHF_RED,
                'VL_coverage': AHF_BLACK
            }
        )
        fig8.update_traces(
            mode='lines+markers+text',
            texttemplate='%{y:.1f}%',
            textposition='top center',
            line=dict(width=2.5),
            marker=dict(size=9)
        )
        fig8.add_hline(y=95, line_dash="dash", line_color=AHF_DARK_RED, line_width=2,
                       annotation_text="Target 95%", annotation_position="top left",
                       annotation_font_color=AHF_DARK_RED)
        ahf_layout(fig8, xaxis_title="Month", yaxis_title="Percentage (%)")
        fig8.update_layout(legend_title="Indicator", hovermode="x unified")
        fig8.for_each_trace(lambda t: t.update(name=t.name.capitalize()))
        st.plotly_chart(fig8, use_container_width=True)

    # Gauge Charts
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        with st.expander("🎯 Census Progress", expanded=False):
            fig, pct, remaining = plot_gauge("Census Progress", actual_census, 7098, AHF_RED)
            st.plotly_chart(fig, use_container_width=True)
            st.progress(min(int(pct), 100))
            c1, c2 = st.columns(2)
            c1.metric("Actual", f"{actual_census:,}")
            c2.metric("Remaining", f"{remaining:,}")

    with col_g2:
        with st.expander("🎯 CRPDDP Progress", expanded=False):
            fig, pct, remaining = plot_gauge("CRPDDP Progress", 322, 600, AHF_BLACK)
            st.plotly_chart(fig, use_container_width=True)
            st.progress(min(int(pct), 100))
            c1, c2 = st.columns(2)
            c1.metric("Actual", "322")
            c2.metric("Remaining", f"{remaining:,}")

# ---------------------------- Footer ----------------------------
st.markdown("---")
st.markdown(f"""
<div class="custom-footer">
    <span class="ahf-logo-text">⚕ AIDS Healthcare Foundation</span><br>
    © 2026 Rich Data Analytics &nbsp;|&nbsp; Powered by AHF Uganda Program
</div>
""", unsafe_allow_html=True)
