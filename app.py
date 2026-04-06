import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Paid Campaign Dashboard", layout="wide")

st.title("🎯 Performance Marketing Dashboard")

# --- LOAD DATA ---
data_file = "master_data.csv"

if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    st.error("master_data.csv not found")
    st.stop()

# --- CLEAN COLUMN NAMES ---
df.columns = df.columns.str.strip().str.lower()

# --- ENSURE REQUIRED COLUMNS ---
required_cols = [
    'date','platform','campaign','spend','impressions','clicks',
    'leads','qualified_leads','sales','revenue'
]

for col in required_cols:
    if col not in df.columns:
        df[col] = 0

# --- TYPE FIX ---
df['date'] = pd.to_datetime(df['date'], errors='coerce')

numeric_cols = ['spend','impressions','clicks','leads','qualified_leads','sales','revenue']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")

platforms = df['platform'].unique().tolist()
selected_platforms = st.sidebar.multiselect("Select Platform", platforms, default=platforms)

filtered_df = df[df['platform'].isin(selected_platforms)]

campaigns = filtered_df['campaign'].unique().tolist()
selected_campaigns = st.sidebar.multiselect("Select Campaign", campaigns, default=campaigns)

filtered_df = filtered_df[filtered_df['campaign'].isin(selected_campaigns)]

# --- KPI METRICS ---
total_spend = filtered_df['spend'].sum()
total_leads = filtered_df['leads'].sum()
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()

cpl = total_spend / total_leads if total_leads > 0 else 0
cpa = total_spend / total_sales if total_sales > 0 else 0
roas = total_revenue / total_spend if total_spend > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💸 Spend", f"₹{total_spend:,.0f}")
col2.metric("📥 Leads", f"{int(total_leads)}")
col3.metric("💰 Sales", f"{int(total_sales)}")
col4.metric("📈 Revenue", f"₹{total_revenue:,.0f}")

col5, col6, col7 = st.columns(3)
col5.metric("CPL", f"₹{cpl:,.0f}")
col6.metric("CPA", f"₹{cpa:,.0f}")
col7.metric("ROAS", f"{roas:.2f}")

st.markdown("---")

# --- CHANNEL PERFORMANCE ---
st.subheader("📊 Channel Performance")

channel_df = filtered_df.groupby('platform').agg({
    'spend':'sum',
    'leads':'sum',
    'sales':'sum',
    'revenue':'sum'
}).reset_index()

channel_df['CPL'] = channel_df['spend'] / channel_df['leads']
channel_df['CPA'] = channel_df['spend'] / channel_df['sales']
channel_df['ROAS'] = channel_df['revenue'] / channel_df['spend']

st.dataframe(channel_df, use_container_width=True)

st.markdown("---")

# --- CAMPAIGN PERFORMANCE ---
st.subheader("🎯 Campaign Performance")

campaign_df = filtered_df.groupby(['campaign','platform']).agg({
    'spend':'sum',
    'leads':'sum',
    'qualified_leads':'sum',
    'sales':'sum',
    'revenue':'sum'
}).reset_index()

campaign_df['CPL'] = campaign_df['spend'] / campaign_df['leads']
campaign_df['ROAS'] = campaign_df['revenue'] / campaign_df['spend']

st.dataframe(campaign_df.sort_values(by="spend", ascending=False), use_container_width=True)

st.markdown("---")

# --- FUNNEL ---
st.subheader("🔁 Lead Funnel")

total_qualified = filtered_df['qualified_leads'].sum()

funnel_df = pd.DataFrame({
    'Stage': ['Leads', 'Qualified', 'Sales'],
    'Count': [total_leads, total_qualified, total_sales]
})

st.bar_chart(funnel_df.set_index('Stage'))

st.markdown("---")

# --- VISUALS ---
colA, colB = st.columns(2)

with colA:
    st.subheader("Spend by Platform")
    fig1 = px.pie(channel_df, values='spend', names='platform', hole=0.5)
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    st.subheader("Revenue vs Spend")
    fig2 = px.scatter(
        campaign_df,
        x="spend",
        y="revenue",
        size="leads",
        color="platform",
        hover_name="campaign"
    )
    st.plotly_chart(fig2, use_container_width=True)