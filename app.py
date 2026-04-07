import streamlit as st
import pandas as pd
import plotly.express as px
import os

def start_section(title):
    st.markdown(f"""
    <div style="
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-top: 20px;
    ">
        <h3>{title}</h3>
    """, unsafe_allow_html=True)

def end_section():
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<style>
.main {
    background-color: #f6f8fb;
}
</style>
""", unsafe_allow_html=True)
# --- PAGE CONFIG ---
st.set_page_config(page_title="Marketing + Sales Dashboard", layout="wide")

st.title("🎯 Performance Marketing + Sales Dashboard")

# --- LOAD DATA ---
data_file = "master_data.csv"

if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    st.error("master_data.csv not found")
    st.stop()

# --- CLEAN ---
df.columns = df.columns.str.strip().str.lower()

numeric_cols = ['spend','leads','not_connected','prospect','not_relevant','enrolled','revenue']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

df['date'] = pd.to_datetime(df['date'])

# --- SIDEBAR ---
st.sidebar.header("Filters")

platforms = df['platform'].unique().tolist()
selected_platforms = st.sidebar.multiselect("Platform", platforms, default=platforms)

filtered_df = df[df['platform'].isin(selected_platforms)]

campaigns = filtered_df['campaign'].unique().tolist()
selected_campaigns = st.sidebar.multiselect("Campaign", campaigns, default=campaigns)

filtered_df = filtered_df[filtered_df['campaign'].isin(selected_campaigns)]

# --- KPI ---
total_spend = filtered_df['spend'].sum()
total_leads = filtered_df['leads'].sum()
total_enrolled = filtered_df['enrolled'].sum()
total_revenue = filtered_df['revenue'].sum()

cpl = total_spend / total_leads if total_leads else 0
cpa = total_spend / total_enrolled if total_enrolled else 0
roas = total_revenue / total_spend if total_spend else 0

st.markdown("""
<style>
.metric-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    text-align: center;
}
.metric-title {
    font-size: 14px;
    color: #888;
}
.metric-value {
    font-size: 26px;
    font-weight: bold;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

def card(title, value):
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# Top row
c1, c2, c3, c4 = st.columns(4)
c1.markdown(card("💸 Spend", f"₹{total_spend:,.0f}"), unsafe_allow_html=True)
c2.markdown(card("📥 Leads", f"{int(total_leads)}"), unsafe_allow_html=True)
c3.markdown(card("🎯 Enrolled", f"{int(total_enrolled)}"), unsafe_allow_html=True)
c4.markdown(card("💰 Revenue", f"₹{total_revenue:,.0f}"), unsafe_allow_html=True)

# Second row
c5, c6, c7 = st.columns(3)
c5.markdown(card("CPL", f"₹{cpl:,.0f}"), unsafe_allow_html=True)
c6.markdown(card("CPA", f"₹{cpa:,.0f}"), unsafe_allow_html=True)
c7.markdown(card("ROAS", f"{roas:.2f}"), unsafe_allow_html=True)

st.markdown("---")

# --- CAMPAIGN TABLE ---

campaign_df = filtered_df.groupby(['platform','campaign']).agg({
    'spend':'sum',
    'leads':'sum',
    'not_connected':'sum',
    'prospect':'sum',
    'not_relevant':'sum',
    'enrolled':'sum',
    'revenue':'sum'
}).reset_index()

st.subheader("📊 Campaign Performance")

st.dataframe(
    campaign_df.sort_values(by="spend", ascending=False),
    use_container_width=True
)
campaign_df['Not Connected %'] = (campaign_df['not_connected'] / campaign_df['leads'] * 100).round(1)
campaign_df['Prospect %'] = (campaign_df['prospect'] / campaign_df['leads'] * 100).round(1)
campaign_df['Not Relevant %'] = (campaign_df['not_relevant'] / campaign_df['leads'] * 100).round(1)
campaign_df['Enrolled %'] = (campaign_df['enrolled'] / campaign_df['leads'] * 100).round(1)

campaign_df['Contact Rate %'] = ((campaign_df['leads'] - campaign_df['not_connected']) / campaign_df['leads'] * 100).round(1)
campaign_df['Conversion %'] = (campaign_df['enrolled'] / campaign_df['leads'] * 100).round(1)

campaign_df['CPL'] = campaign_df['spend'] / campaign_df['leads']
campaign_df['ROAS'] = campaign_df['revenue'] / campaign_df['spend']

st.dataframe(campaign_df.sort_values(by="spend", ascending=False), use_container_width=True)

st.markdown("---")

# --- FUNNEL (FIXED VERSION) ---
st.subheader("🔻 Lead Funnel")

leads = int(total_leads)
contacted = int(total_leads - filtered_df['not_connected'].sum())
prospect = int(filtered_df['prospect'].sum())
enrolled = int(total_enrolled)

contacted_pct = (contacted / leads * 100) if leads else 0
prospect_pct = (prospect / leads * 100) if leads else 0
enrolled_pct = (enrolled / leads * 100) if leads else 0

st.markdown("""
<style>
.funnel {
    width: 70%;
    margin: auto;
    text-align: center;
    font-weight: bold;
}
.stage {
    margin: 15px auto;
    padding: 20px;
    border-radius: 12px;
    font-size: 18px;
}
.stage1 { width: 100%; background: #f9d976; }
.stage2 { width: 80%; background: #f39c12; }
.stage3 { width: 60%; background: #e67e22; color: white; }
.stage4 { width: 40%; background: #d35400; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    f"""
<div class="funnel">
    <div class="stage stage1">Leads: {leads} (100%)</div>
    <div class="stage stage2">Contacted: {contacted} ({contacted_pct:.1f}%)</div>
    <div class="stage stage3">Prospect: {prospect} ({prospect_pct:.1f}%)</div>
    <div class="stage stage4">Enrolled: {enrolled} ({enrolled_pct:.1f}%)</div>
</div>
""",
    unsafe_allow_html=True
)
st.markdown("---")

# --- WEEKLY TREND ---
st.subheader("📅 Weekly Trend")

weekly = filtered_df.groupby(pd.Grouper(key='date', freq='W')).agg({
    'spend':'sum',
    'leads':'sum',
    'enrolled':'sum'
}).reset_index()

st.line_chart(weekly.set_index('date')[['leads','enrolled']])
st.line_chart(weekly.set_index('date')[['spend']])

st.markdown("---")

# --- INSIGHTS ---
st.subheader("🧠 Key Insights")

best = campaign_df.sort_values(by="ROAS", ascending=False).iloc[0]
worst = campaign_df.sort_values(by="ROAS", ascending=True).iloc[0]

st.write(f"🔥 Best Campaign: {best['campaign']} (ROAS: {best['ROAS']:.2f})")
st.write(f"⚠️ Worst Campaign: {worst['campaign']} (ROAS: {worst['ROAS']:.2f})")

st.markdown("---")

# --- PROBLEM DIAGNOSIS ---
st.subheader("🚨 Problem Diagnosis")

for _, row in campaign_df.iterrows():

    if row['Not Connected %'] > 40:
        st.write(f"📞 {row['campaign']} → High Not Connected ({row['Not Connected %']}%) → Sales issue")

    elif row['Not Relevant %'] > 30:
        st.write(f"🎯 {row['campaign']} → High Not Relevant ({row['Not Relevant %']}%) → Targeting issue")

    elif row['Prospect %'] > 40 and row['Conversion %'] < 10:
        st.write(f"🤝 {row['campaign']} → Good interest but low conversion → Closing issue")

    elif row['Conversion %'] > 15:
        st.write(f"🔥 {row['campaign']} → Strong conversion → Scale this")