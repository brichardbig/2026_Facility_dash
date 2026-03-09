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
df = pd.read_excel('facility_data_2026.xlsx')

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

# ----------------------------
# Custom CSS – uniform card size
# ----------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #f0f4f8;
    padding: 20px 16px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    text-align: center;
    height: 150px;                  /* fixed height – main fix */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 16px;
}

.metric-title {
    font-size: 0.95rem;
    color: #6b7280;
    margin-bottom: 10px;
    line-height: 1.2;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.15;
    min-height: 2.4rem;             /* reserves space for 1-2 lines */
}

.metric-value small,
.metric-value span {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 400;
}

.metric-delta-positive,
.metric-delta-negative {
    font-size: 0.9rem;
    margin-top: 8px;
}
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
    options=df['Month'].unique(),
    default=df['Month'].unique()
)
filtered_df = df[df['Month'].isin(selected_months)]

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
        metric_card(
            "Total Positives",
            f"{total_positives:,}<br><small>({avg_yield:.1f}% yield)</small>"
        )

    with col3:
        metric_card(
            "Total ICT",
            f"{total_ict:,}<br><small>({ict_percent:.1f}% of tested)</small>"
        )

    with col4:
        metric_card("Condoms Distributed", f"{total_condoms:,}")

    # --------------------------------------------------
    # Testing Trends
    # --------------------------------------------------
    with st.expander("📈 Testing Trends by Month", expanded=True):
        fig1 = px.bar(
            filtered_df,
            x='Month',
            y='Total_tested',
            text=filtered_df['Total_tested'],
            title="Total Tested by Month"
        )
        fig1.add_hline(
            y=1673,
            line_dash="dash",
            line_color="red",
            annotation_text="Target (1,673)"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --------------------------------------------------
    # Positives & Yield
    # --------------------------------------------------
    with st.expander("Positives & Yield"):
        filtered_df['Yield'] = (filtered_df['Positives'] / filtered_df['Total_tested'] * 100)\
            .replace([np.inf, -np.inf], 0).fillna(0)
        
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
            name="Yield (%)",
            yaxis='y2',
            mode='lines+markers+text',
            text=filtered_df['Yield'].round(1).astype(str) + "%"
        ))
        fig2.update_layout(
            yaxis=dict(title="Positives"),
            yaxis2=dict(title="Yield (%)", overlaying='y', side='right'),
            title="Positives and Yield by Month"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --------------------------------------------------
    # ICT %
    # --------------------------------------------------
    with st.expander("ICT - HTS Percentage"):
        filtered_df['ICT_percentage'] = (filtered_df['ICT_tested'] / filtered_df['Total_tested'] * 100)
        fig3 = px.line(
            filtered_df,
            x='Month',
            y='ICT_percentage',
            markers=True,
            title="ICT Testing Percentage by Month"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --------------------------------------------------
    # ICT TYPES
    # --------------------------------------------------
    with st.expander("ICT Testing Types"):
        df_long = filtered_df.melt(
            id_vars='Month',
            value_vars=['ICT_tested', 'APN_ict', 'SNS'],
            var_name='Testing_Type',
            value_name='Count'
        )
        fig4 = px.bar(
            df_long,
            x='Month',
            y='Count',
            color='Testing_Type',
            barmode='group',
            title="ICT Testing Types"
        )
        st.plotly_chart(fig4, use_container_width=True)

    # --------------------------------------------------
    # Linkage
    # --------------------------------------------------
    with st.expander("Linkage to Care (%)"):
        filtered_df['Linkage'] = (filtered_df['Linked'] / filtered_df['Positives'] * 100)
        fig5 = px.line(
            filtered_df,
            x='Month',
            y='Linkage',
            markers=True,
            title="Linkage to Care (%)"
        )
        st.plotly_chart(fig5, use_container_width=True)

    # --------------------------------------------------
    # Condom Table
    # --------------------------------------------------
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

    actual_census = 6712
    net_growth = (
        filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']
    ).sum() - (
        filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']
    ).sum()
    
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

    
    # --------------------------------------------------
    # Net Growth Table
    # --------------------------------------------------
    net_growth_table = filtered_df[['Month', 'Newly_diagnosed', 'TI', 'Returned', 'LTFU', 'TO', 'Dead', 'Net_Growth']]
    net_growth_table['Target'] = 45  # Add target column
    st.subheader("Net Growth Table")
    st.dataframe(net_growth_table, use_container_width=True)

    
    # --------------------------------------------------
    # Net Growth
    # --------------------------------------------------
    with st.expander("Net Growth by Month", expanded=True):
        filtered_df['Net_Growth'] = (
            filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']
        ) - (
            filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']
        )
        fig6 = px.area(
            filtered_df,
            x='Month',
            y='Net_Growth',
            markers=True,
            title="Net Growth by Month"
        )
        st.plotly_chart(fig6, use_container_width=True)

    # --------------------------------------------------
    # Attrition
    # --------------------------------------------------
    with st.expander("Attrition by Month"):
        filtered_df['Total_Attrition'] = filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']
        fig7 = px.bar(
            filtered_df,
            x='Month',
            y=['LTFU', 'TO', 'Dead', 'Total_Attrition'],
            barmode='group',
            title="Attrition by Month"
        )
        st.plotly_chart(fig7, use_container_width=True)

       
    # --------------------------------------------------
    # Viral Suppression
    # --------------------------------------------------
    with st.expander("Viral Suppression by Month"):
        fig8 = px.line(
            filtered_df,
            x='Month',
            y='suppression',
            markers=True,
            title="Viral Suppression by Month"
        )
        fig8.add_hline(y=95, line_dash="dash", line_color="red")
        st.plotly_chart(fig8, use_container_width=True)

    # --------------------------------------------------
    # Gauges
    # --------------------------------------------------
    col_g1, col_g2 = st.columns(2)

    def plot_gauge(title, actual, target, color):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=actual,
            delta={'reference': target},
            gauge={
                'axis': {'range': [0, target]},
                'bar': {'color': color},
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'value': target
                }
            },
            title={'text': title}
        ))
        fig.update_layout(height=300)
        return fig

    with col_g1:
        with st.expander("🎯 Census Progress"):
            st.plotly_chart(
                plot_gauge("Census Progress", actual_census, 7098, "purple"),
                use_container_width=True
            )

    with col_g2:
        with st.expander("🎯 CRPDDP Progress"):
            st.plotly_chart(
                plot_gauge("CRPDDP Progress", 267, 700, "green"),
                use_container_width=True
            )

# ----------------------------
# Footer
# ----------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6b7280; font-size:0.95rem; margin-top:40px; padding:20px 0;">
© 2026 Rich Data Analytics – Facility Performance Dashboard
</div>
""", unsafe_allow_html=True)

