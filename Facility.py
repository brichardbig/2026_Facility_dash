import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(page_title="2026 Performance Dashboard", layout="wide")
st.title("📊 2026 Facility Performance Dashboard")

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    return df

df = load_data('facility_data_2026.xlsx')

# ----------------------------
# Preprocessing
# ----------------------------
df['VL_coverage'] = df['VL_coverage'] * 100
df['suppression'] = df['suppression'] * 100

cols_to_round = [
    'Total_tested', 'Positives', 'ICT_tested', 'APN_ict', 'SNS', 'Linked',
    'condom_distribution', 'Newly_diagnosed', 'TI', 'Returned',
    'LTFU', 'TO', 'Dead', 'CRPDDP'
]
df[cols_to_round] = df[cols_to_round].astype('Int64')

# Sort months chronologically
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
if all(m in month_order for m in df['Month'].unique()):
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
    df = df.sort_values('Month')

# ----------------------------
# Custom CSS – blue theme + delta colors
# ----------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #1D4ED8;
    padding: 20px 16px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    text-align: center;
    height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 16px;
    color: white;
}
.metric-title {
    font-size: 0.95rem;
    color: #BFDBFE;
    margin-bottom: 10px;
    line-height: 1.2;
}
.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: white;
    line-height: 1.15;
    min-height: 2.4rem;
}
.metric-value small,
.metric-value span {
    font-size: 0.85rem;
    color: #BFDBFE;
    font-weight: 400;
}
.metric-delta-positive { color: #10B981 !important; font-weight: 600; }
.metric-delta-negative { color: #EF4444 !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Metric Card Function
# ----------------------------
def metric_card(title, value, delta=None):
    delta_html = ""
    if delta is not None:
        color_class = "metric-delta-positive" if delta >= 0 else "metric-delta-negative"
        delta_html = f'<div class="{color_class}">{delta:+,}</div>'

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

# ----------------------------
# Sidebar Filter
# ----------------------------
st.sidebar.header("Filters")
selected_months = st.sidebar.multiselect(
    "Select Months",
    options=sorted(df['Month'].unique()),  # sorted for better UX
    default=df['Month'].unique()
)
filtered_df = df[df['Month'].isin(selected_months)].copy()

# ----------------------------
# Tabs
# ----------------------------
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Tested", f"{total_tested:,}")

    with col2:
        metric_card("Total Positives", f"{total_positives:,}<br><small>({avg_yield:.1f}% yield)</small>")

    with col3:
        metric_card("Total ICT", f"{total_ict:,}<br><small>({ict_percent:.1f}% of tested)</small>")

    with col4:
        metric_card("Condoms Distributed", f"{total_condoms:,}")

    # Charts (with text labels improved)
    with st.expander("📈 Testing Trends by Month", expanded=True):
        fig1 = px.bar(filtered_df, x='Month', y='Total_tested', text=filtered_df['Total_tested'])
        fig1.update_traces(textposition='outside')
        fig1.add_hline(y=1673, line_dash="dash", line_color="red", annotation_text="Target (1,673)")
        st.plotly_chart(fig1, use_container_width=True)

    # ... (rest of prevention charts remain mostly unchanged - just make sure textposition is set correctly)

# ==================================================
# CARE & TREATMENT TAB
# ==================================================
with tab2:
    st.header("Care and Treatment Metrics")

    # Calculate Net Growth **once**
    filtered_df['Net_Growth'] = (
        filtered_df['Newly_diagnosed'].fillna(0) +
        filtered_df['TI'].fillna(0) +
        filtered_df['Returned'].fillna(0)
    ) - (
        filtered_df['LTFU'].fillna(0) +
        filtered_df['TO'].fillna(0) +
        filtered_df['Dead'].fillna(0)
    )

    actual_census   = 6712
    net_growth      = filtered_df['Net_Growth'].sum()
    total_ltfu      = filtered_df['LTFU'].sum()
    total_attrition = (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']).sum()
    ltfu_percent    = (total_ltfu / total_attrition * 100) if total_attrition > 0 else 0
    avg_suppression = filtered_df['suppression'].mean()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1: metric_card("Actual Census", f"{actual_census:,}")
    with col2: metric_card("Net Growth", f"{net_growth:,}")
    with col3: metric_card("LTFU", f"{total_ltfu:,}")
    with col4: metric_card("LTFU % of Attrition", f"{ltfu_percent:.1f}%")
    with col5: metric_card("Viral Suppression (%)", f"{avg_suppression:.1f}%")

    # Net Growth Chart
    with st.expander("Net Growth by Month", expanded=True):
        fig6 = px.area(filtered_df, x='Month', y='Net_Growth', markers=True, text=filtered_df['Net_Growth'])
        fig6.update_traces(textposition='top center')
        st.plotly_chart(fig6, use_container_width=True)

    # Attrition Chart – fixed text parameter
    with st.expander("Attrition by Month"):
        filtered_df['Total_Attrition'] = filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']
        fig7 = px.bar(
            filtered_df,
            x='Month',
            y=['LTFU', 'TO', 'Dead', 'Total_Attrition'],
            barmode='group',
            title="Attrition by Month"
        )
        # Add text labels – one trace at a time
        for trace in fig7.data:
            trace.update(text=trace.y, textposition='outside')
        st.plotly_chart(fig7, use_container_width=True)

    # Net Growth Details Table
    with st.expander("📋 Net Growth Details", expanded=True):
        net_growth_table = filtered_df[[
            'Month', 'Newly_diagnosed', 'TI', 'Returned',
            'LTFU', 'TO', 'Dead', 'Net_Growth'
        ]].copy()

        net_growth_table = net_growth_table.rename(columns={
            'Newly_diagnosed': 'New Diagnosed',
            'TI': 'Transferred In',
            'Returned': 'Returned',
        })

        net_growth_table['Target'] = 45
        net_growth_table['% Achieved'] = (net_growth_table['Net_Growth'] / 45 * 100).round(1).astype(str) + ' %'

        st.dataframe(
            net_growth_table.style.format("{:,}", subset=[
                'New Diagnosed', 'TI', 'Returned', 'LTFU', 'TO', 'Dead', 'Net_Growth'
            ]),
            use_container_width=True,
            hide_index=True
        )

    # Viral Suppression
    with st.expander("Viral Suppression by Month"):
        fig8 = px.line(filtered_df, x='Month', y='suppression', markers=True,
                       text=filtered_df['suppression'].round(1).astype(str) + "%")
        fig8.update_traces(textposition='top center')
        fig8.add_hline(y=95, line_dash="dash", line_color="red")
        st.plotly_chart(fig8, use_container_width=True)

    # Gauges (unchanged)
    col_g1, col_g2 = st.columns(2)
    def plot_gauge(title, actual, target, color):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=actual,
            delta={'reference': target},
            gauge={'axis': {'range': [0, target]}, 'bar': {'color': color},
                   'threshold': {'line': {'color': "red", 'width': 4}, 'value': target}},
            title={'text': title}
        ))
        fig.update_layout(height=300)
        return fig

    with col_g1:
        with st.expander("🎯 Census Progress"):
            st.plotly_chart(plot_gauge("Census Progress", actual_census, 7098, "purple"), use_container_width=True)
    with col_g2:
        with st.expander("🎯 CRPDDP Progress"):
            st.plotly_chart(plot_gauge("CRPDDP Progress", 267, 700, "green"), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6b7280; font-size:0.95rem; margin-top:40px; padding:20px 0;">
© 2026 Rich Data Analytics – Facility Performance Dashboard
</div>
""", unsafe_allow_html=True)
