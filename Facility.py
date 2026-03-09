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

# Sidebar filters
st.sidebar.header("Filters")
selected_months = st.sidebar.multiselect("Select Months", df['Month'].unique(), default=df['Month'].unique())
filtered_df = df[df['Month'].isin(selected_months)]

# Tabs for Prevention & Care
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
    col1.metric("Total Tested", f"{total_tested:,}", delta=f"{1673 - total_tested}")
    col2.metric("Total Positives", f"{total_positives:,}", delta=f"{53 - total_positives}")
    col3.metric("Average Yield (%)", f"{avg_yield:.1f}%")
    col4.metric("Condoms Distributed", f"{total_condoms:,}", delta=f"{16730 - total_condoms}")

    with st.expander("📈 Testing Trends by Month", expanded=True):
        fig1 = px.bar(
            filtered_df, 
            x='Month', 
            y='Total_tested', 
            text=filtered_df['Total_tested'].apply(lambda x: f"{x:,}" if pd.notna(x) else ""),
            title='Total Tested by Month'
        )
        fig1.update_traces(textposition='auto', textfont_size=11)
        fig1.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
        fig1.add_hline(y=1673, line_dash="dash", line_color="red", annotation_text="Target (1,673)")
        st.plotly_chart(fig1, use_container_width=True)

    with st.expander("Positives & Yield"):
        filtered_df['Yield'] = (filtered_df['Positives'] / filtered_df['Total_tested'] * 100).replace([np.inf, -np.inf], 0).fillna(0)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=filtered_df['Month'], 
                y=filtered_df['Positives'], 
                name="Positives",
                text=filtered_df['Positives'].apply(lambda x: f"{x:,}" if pd.notna(x) and x > 0 else ""),
                textposition='auto'
            )
        )
        fig2.add_trace(
            go.Scatter(
                x=filtered_df['Month'], 
                y=filtered_df['Yield'], 
                name="Yield (%)", 
                mode='lines+markers+text',
                text=filtered_df['Yield'].round(1).astype(str) + '%',
                textposition='top center',
                yaxis='y2',
                line=dict(color='orange'),
                marker=dict(size=8)
            )
        )
        fig2.update_layout(
            title="Positives and Yield by Month",
            yaxis=dict(title="Positives"),
            yaxis2=dict(title="Yield (%)", overlaying='y', side='right'),
            uniformtext_minsize=10,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
        fig3.update_traces(textposition='top center', line=dict(width=2.5), marker=dict(size=9))
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
            text=df_long['Count'].apply(lambda x: f"{int(x):,}" if x > 0 else "")
        )
        fig4.update_traces(textposition='auto', textfont_size=11)
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
        fig5.update_traces(textposition='top center', line=dict(width=2.5), marker=dict(size=9))
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
    col1.metric("Actual Census", f"{actual_census:,}")
    col2.metric("Net Growth", f"{net_growth:,}")
    col3.metric("LTFU", f"{total_ltfu:,}")
    col4.metric("LTFU % of Attrition", f"{ltfu_percent:.1f}%")
    col5.metric("Viral Suppression (%)", f"{avg_suppression:.1f}%")

    with st.expander("Net Growth by Month", expanded=True):
        filtered_df['Net_Growth'] = (filtered_df['Newly_diagnosed'] + filtered_df['TI'] + filtered_df['Returned']) - \
                                    (filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead'])
        fig6 = px.area(
            filtered_df, 
            x='Month', 
            y='Net_Growth', 
            markers=True, 
            title="Net Growth by Month",
            text=filtered_df['Net_Growth'].apply(lambda x: f"{x:+,}" if pd.notna(x) and x != 0 else "0")
        )
        fig6.update_traces(textposition='top center', textfont_size=11)
        st.plotly_chart(fig6, use_container_width=True)

    with st.expander("Attrition by Month"):
        # Calculate total attrition per month
        filtered_df['Total_Attrition'] = filtered_df['LTFU'] + filtered_df['TO'] + filtered_df['Dead']

        fig7 = go.Figure()

        # Add grouped bars for each attrition type
        colors = {'LTFU': '#EF553B', 'TO': '#636EFA', 'Dead': '#AB63FA'}
        for attrition_type in ['LTFU', 'TO', 'Dead']:
            fig7.add_trace(go.Bar(
                x=filtered_df['Month'],
                y=filtered_df[attrition_type],
                name=attrition_type,
                marker_color=colors[attrition_type],
                text=filtered_df[attrition_type].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x > 0 else ""),
                textposition='auto',
                textfont_size=11
            ))

        # Add total attrition as a grouped bar
        fig7.add_trace(go.Bar(
            x=filtered_df['Month'],
            y=filtered_df['Total_Attrition'],
            name='Total Attrition',
            marker_color='#FF7F0E',
            text=filtered_df['Total_Attrition'].apply(lambda x: f"{int(x):,}" if pd.notna(x) and x > 0 else ""),
            textposition='auto',
            textfont=dict(size=11, color='black'),
        ))

        fig7.update_layout(
            title="Attrition by Month",
            barmode='group',
            yaxis=dict(title="Count"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            uniformtext_minsize=10
        )
        st.plotly_chart(fig7, use_container_width=True)

    with st.expander("Viral Suppression by Month"):
        fig8 = px.line(
            filtered_df, 
            x='Month', 
            y='suppression', 
            markers=True, 
            title="Viral Suppression by Month",
            text=filtered_df['suppression'].round(1).astype(str) + '%'
        )
        fig8.update_traces(textposition='top center', line=dict(width=2.5), marker=dict(size=9))
        fig8.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Target (95%)")
        st.plotly_chart(fig8, use_container_width=True)

    # Gauge Charts
    col_g1, col_g2 = st.columns(2)
    
    def plot_gauge(title, actual, target, color="blue"):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=actual,
            number={'font': {'size': 36}},
            delta={'reference': target, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, target]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, target*0.5], 'color': 'lightgrey'},
                    {'range': [target*0.5, target], 'color': 'lightblue'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': target
                }
            },
            title={'text': title, 'font': {'size': 20}}
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
        return fig

    with col_g1:
        with st.expander("🎯 Census Progress"):
            st.plotly_chart(plot_gauge("Census Progress", actual=actual_census, target=7098, color="purple"), use_container_width=True)
    
    with col_g2:
        with st.expander("🎯 CRPDDP Progress"):

            st.plotly_chart(plot_gauge("CRPDDP Progress", actual=267, target=700, color="green"), use_container_width=True)

    # ────────────────────────────────────────────────
# Footer / Copyright
# ────────────────────────────────────────────────
st.markdown("---")  # horizontal line (optional but looks nice)

st.markdown(
    """
    <div style="
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: 40px;
        padding: 20px 0;
    ">
        © 2026 Rich Data Analytics – Facility Performance Dashboard
    </div>
    """,
    unsafe_allow_html=True
)


