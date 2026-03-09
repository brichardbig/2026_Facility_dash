import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = pd.read_excel('facility_data_2026.xlsx')

# Preprocessing
df['VL_coverage'] = df['VL_coverage'] * 100
df['suppression'] = df['suppression'] * 100
cols_to_round = ['Total_tested', 'Positives', 'ICT_tested', 'APN_ict', 'SNS', 'Linked',
                 'condom_distribution', 'Newly_diagnosed', 'TI', 'Returned', 'LTFU', 'TO', 'Dead', 'CRPDDP']
df[cols_to_round] = df[cols_to_round].astype('Int64')

# Streamlit layout
st.set_page_config(page_title="2026 Performance Dashboard", layout="wide")
st.title("📊 2026 Facility Performance Dashboard")

# Custom CSS for styling
st.markdown("""
<style>

.metric-card {
    border-radius: 12px;
    padding: 18px;
    background-color: #f0f4f8;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 10px;
    text-align: center;
}

.metric-title {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #111827;
}

.metric-delta-positive {
    color: green;
    font-size: 0.85rem;
}

.metric-delta-negative {
    color: red;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)

# Metric Card Function
def metric_card(title, value, delta=None):
    delta_html = ""
    if delta is not None:
        if delta >= 0:
            delta_html = f'<div class="metric-delta-positive">▲ {abs(delta):,}</div>'
        else:
            delta_html = f'<div class="metric-delta-negative">▼ {abs(delta):,}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Filters")
selected_months = st.sidebar.multiselect("Select Months", df['Month'].unique(), default=df['Month'].unique())
filtered_df = df[df['Month'].isin(selected_months)]

# Tabs
tab1, tab2 = st.tabs(["🩺 Prevention", "💊 Care & Treatment"])

# --------------------------
# Prevention Tab
# --------------------------
with tab1:

    st.header("Prevention Metrics")

    total_tested = filtered_df['Total_tested'].sum()
    total_positives = filtered_df['Positives'].sum()
    avg_yield = (total_positives / total_tested * 100) if total_tested > 0 else 0
    total_condoms = filtered_df['condom_distribution'].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Tested", f"{total_tested:,}", 1673 - total_tested)

    with col2:
        metric_card("Total Positives", f"{total_positives:,}", 53 - total_positives)

    with col3:
        metric_card("Average Yield (%)", f"{avg_yield:.1f}%")

    with col4:
        metric_card("Condoms Distributed", f"{total_condoms:,}", 16730 - total_condoms)

    with st.expander("📈 Testing Trends by Month", expanded=True):
        fig1 = px.bar(
            filtered_df,
            x='Month',
            y='Total_tested',
            text=filtered_df['Total_tested'].apply(lambda x: f"{x:,}" if pd.notna(x) else ""),
            title='Total Tested by Month'
        )
        fig1.update_traces(textposition='auto', textfont_size=11)
        fig1.add_hline(y=1673, line_dash="dash", line_color="red", annotation_text="Target (1,673)")
        st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Positives & Yield"):
        filtered_df['Yield'] = (filtered_df['Positives'] / filtered_df['Total_tested'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=filtered_df['Month'],
            y=filtered_df['Positives'],
            name="Positives",
            text=filtered_df['Positives'].apply(lambda x: f"{x:,}" if pd.notna(x) and x > 0 else ""),
            textposition='auto'
        ))
        fig2.add_trace(go.Scatter(
            x=filtered_df['Month'],
            y=filtered_df['Yield'],
            name="Yield (%)",
            mode='lines+markers+text',
            text=filtered_df['Yield'].round(1).astype(str) + '%',
            textposition='top center',
            yaxis='y2',
            line=dict(color='orange'),
            marker=dict(size=8)
        ))
        fig2.update_layout(
            title="Positives and Yield by Month",
            yaxis=dict(title="Positives"),
            yaxis2=dict(title="Yield (%)", overlaying='y', side='right')
        )
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("ICT - HTS Percentage"):
        filtered_df['ICT_percentage'] = (filtered_df['ICT_tested'] / filtered_df['Total_tested'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        fig3 = px.line(
            filtered_df,
            x='Month',
            y='ICT_percentage',
            markers=True,
            title="ICT Testing Percentage by Month",
            text=filtered_df['ICT_percentage'].round(1).astype(str) + '%'
        )
        fig3.update_traces(textposition='top center')
        st.plotly_chart(fig3, use_container_width=True)

    with st.expander("ICT Testing Types"):
        df_long = filtered_df.melt(id_vars='Month', value_vars=['ICT_tested', 'APN_ict', 'SNS'],
                                   var_name='Testing_Type', value_name='Count')
        fig4 = px.bar(
            df_long,
            x='Month',
            y='Count',
            color='Testing_Type',
            barmode='group',
            title="ICT Testing Types",
            text=df_long['Count']
        )
        fig4.update_traces(textposition='auto')
        st.plotly_chart(fig4, use_container_width=True)

    with st.expander("Linkage to Care (%)"):
        filtered_df['Linkage'] = (filtered_df['Linked'] / filtered_df['Positives'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        fig5 = px.line(
            filtered_df,
            x='Month',
            y='Linkage',
            markers=True,
            title="Linkage to Care (%)",
            text=filtered_df['Linkage'].round(1).astype(str) + '%'
        )
        fig5.update_traces(textposition='top center')
        st.plotly_chart(fig5, use_container_width=True)

    with st.expander("🧷 Condom Distribution by Month"):
        condom_table = filtered_df[['Month', 'condom_distribution']].copy()
        condom_table['Target'] = 16730
        condom_table['% Achieved'] = (condom_table['condom_distribution'] / 16730 * 100).fillna(0)
        st.dataframe(
            condom_table.style.format({
                "condom_distribution": "{:,}",
                "% Achieved": "{:.1f}%"
            }),
            use_container_width=True
        )

# --------------------------
# Care & Treatment Tab
# --------------------------
with tab2:

    st.header("Care and Treatment Metrics")

    actual_census = 6712
    net_growth = (filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']).sum() - \
                 (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']).sum()
    total_ltfu = filtered_df['LTFU'].sum()
    total_attrition = (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']).sum()
    ltfu_percent = (total_ltfu / total_attrition * 100) if total_attrition != 0 else 0
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

    # (All the rest of your charts and gauges remain exactly the same)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;color:#6b7280;font-size:0.95rem;margin-top:40px;padding:20px 0;">
        © 2026 Rich Data Analytics – Facility Performance Dashboard
    </div>
    """,
    unsafe_allow_html=True
)


