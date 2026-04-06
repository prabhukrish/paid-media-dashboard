import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

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

c1, c2, c3, c4 = st.columns(4)
c1.metric("💸 Spend", f"₹{total_spend:,.0f}")
c2.metric("📥 Leads", int(total_leads))
c3.metric("🎯 Enrolled", int(total_enrolled))
c4.metric("💰 Revenue", f"₹{total_revenue:,.0f}")

c5, c6, c7 = st.columns(3)
c5.metric("CPL", f"₹{cpl:,.0f}")
c6.metric("CPA", f"₹{cpa:,.0f}")
c7.metric("ROAS", f"{roas:.2f}")

st.markdown("---")

# --- CAMPAIGN TABLE ---
st.subheader("📊 Campaign Performance")

campaign_df = filtered_df.groupby(['platform','campaign']).agg({
    'spend':'sum',
    'leads':'sum',
    'not_connected':'sum',
    'prospect':'sum',
    'not_relevant':'sum',
    'enrolled':'sum',
    'revenue':'sum'
}).reset_index()

# % metrics
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

# --- PREMIUM FUNNEL (HTML STYLE) ---
st.subheader("🔻 Lead Funnel")

leads = int(total_leads)
contacted = int(total_leads - filtered_df['not_connected'].sum())
prospect = int(filtered_df['prospect'].sum())
enrolled = int(total_enrolled)

st.markdown(f"""
<style>
.funnel {{
    width: 70%;
    margin: auto;
    text-align: center;
    font-weight: bold;
    color: #333;
}}
.stage {{
    margin: 12px auto;
    padding: 18px;
    border-radius: 12px;
    font-size: 18px;
}}
.stage1 {{ width: 100%; background: #f9d976; }}
.stage2 {{ width: 80%; background: #f39c12; }}
.stage3 {{ width: 60%; background: #e67e22; color: white; }}
.stage4 {{ width: 40%; background: #d35400; color: white; }}
</style>

<div class="funnel">
    <div class="stage stage1">Leads: {leads}</div>
    <div class="stage stage2">Contacted: {contacted}</div>
    <div class="stage stage3">Prospect: {prospect}</div>
    <div class="stage stage4">Enrolled: {enrolled}</div>
</div>
""", unsafe_allow_html=True)

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

# --- PROBLEM DIAGNOSIS ---
st.markdown("---")
st.subheader("🚨 Problem Diagnosis")

for _, row in campaign_df.iterrows():

    if row['Not Connected %'] > 40:
        st.write(f"📞 {row['campaign']} → High Not Connected ({row['Not Connected %']}%) → Sales follow-up issue")

    elif row['Not Relevant %'] > 30:
        st.write(f"🎯 {row['campaign']} → High Not Relevant ({row['Not Relevant %']}%) → Targeting issue")

    elif row['Prospect %'] > 40 and row['Conversion %'] < 10:
        st.write(f"🤝 {row['campaign']} → Good interest but low conversion → Closing issue")

    elif row['Conversion %'] > 15:
        st.write(f"🔥 {row['campaign']} → Strong conversion → Scale this campaign")