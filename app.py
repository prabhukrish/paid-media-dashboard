import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Revenue Dashboard", layout="wide")
st.title("🎯 Marketing + Sales Dashboard")

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

# --- FILTERS ---
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
c1.metric("Spend", f"₹{total_spend:,.0f}")
c2.metric("Leads", int(total_leads))
c3.metric("Enrolled", int(total_enrolled))
c4.metric("Revenue", f"₹{total_revenue:,.0f}")

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

# % CALCULATIONS
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

# --- FUNNEL ---
st.subheader("🔁 Lead Status Funnel")

funnel = pd.DataFrame({
    'Stage': ['Leads','Not Connected','Prospect','Not Relevant','Enrolled'],
    'Count': [
        total_leads,
        filtered_df['not_connected'].sum(),
        filtered_df['prospect'].sum(),
        filtered_df['not_relevant'].sum(),
        total_enrolled
    ]
})


st.markdown("---")
st.subheader("🔻 Lead Funnel")

funnel_df = pd.DataFrame({
    'Stage': ['Leads','Contacted','Prospect','Enrolled'],
    'Count': [
        total_leads,
        total_leads - filtered_df['not_connected'].sum(),
        filtered_df['prospect'].sum(),
        total_enrolled
    ]
})

import plotly.graph_objects as go

st.markdown("---")
st.subheader("🔻 Lead Funnel (Visual)")

# Funnel Data (clean version)
leads = total_leads
contacted = total_leads - filtered_df['not_connected'].sum()
prospect = filtered_df['prospect'].sum()
enrolled = total_enrolled

stages = ["Leads", "Contacted", "Prospect", "Enrolled"]
values = [leads, contacted, prospect, enrolled]

# Color gradient (top → bottom)
colors = ["#f9d976", "#f39c12", "#e67e22", "#d35400"]

fig = go.Figure(go.Funnel(
    y = stages,
    x = values,
    textinfo = "value+percent initial",
    marker = {"color": colors},
    opacity = 0.95
))

fig.update_layout(
    height=500,
    margin=dict(l=50, r=50, t=30, b=30),
    funnelmode="stack",
)

st.plotly_chart(fig, use_container_width=True)

st.plotly_chart(fig, use_container_width=True)

# --- WEEKLY TREND ---
st.subheader("📅 Weekly Trend")

weekly = filtered_df.groupby(pd.Grouper(key='date', freq='W')).sum().reset_index()

st.line_chart(weekly.set_index('date')[['leads','enrolled']])
st.line_chart(weekly.set_index('date')[['spend']])

st.markdown("---")

# --- INSIGHTS ---
st.subheader("🧠 Key Insights")

best = campaign_df.sort_values(by="ROAS", ascending=False).iloc[0]
worst = campaign_df.sort_values(by="ROAS", ascending=True).iloc[0]

st.write(f"🔥 Best Campaign: {best['campaign']} (ROAS: {best['ROAS']:.2f})")
st.write(f"⚠️ Worst Campaign: {worst['campaign']} (ROAS: {worst['ROAS']:.2f})")

low_conv = campaign_df[campaign_df['Conversion %'] < 10]

for _, row in low_conv.iterrows():
    st.write(f"🚨 Low Conversion: {row['campaign']} ({row['Conversion %']}%)")


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