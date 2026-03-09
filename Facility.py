# ---------------------------- Custom CSS ----------------------------
st.markdown("""
<style>
/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #e0f2fe, #bae6fd);
    padding: 20px 16px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    text-align: center;
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.12);
}
.metric-title {
    font-size: 1rem;
    font-weight: 500;
    color: #1e3a8a;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.metric-value small, .metric-value span {
    font-size: 0.85rem;
    color: #334155;
    font-weight: 400;
}
.metric-delta-positive {
    color: #16a34a;
    font-weight: 600;
    margin-top: 6px;
}
.metric-delta-negative {
    color: #dc2626;
    font-weight: 600;
    margin-top: 6px;
}

/* Tabs */
.stTabs [role="tab"] {
    font-weight: 600;
    font-size: 1rem;
    color: #1e40af;
}

/* Expanders */
.stExpander > div:first-child {
    background-color: #f1f5f9;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 12px;
}
.stExpander > div:first-child:hover {
    background-color: #e2e8f0;
}

/* Footer */
footer {
    visibility: hidden;
}
.custom-footer {
    text-align: center;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 40px;
    padding: 20px 0;
}
</style>
""", unsafe_allow_html=True)
