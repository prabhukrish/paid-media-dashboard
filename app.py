import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

st.title("🎯 Performance Marketing Dashboard")

# --- LOAD DATA ---
data_file = "master_data.csv"

if os.path.exists(data_file):
    df = pd.read_csv(data_file)
else:
    st.error("master_data.csv not found")
    st.stop()

# --- CLEAN COLUMN NAMES ---
df.columns = df.columns.str.strip()

# --- STANDARDIZE (IMPORTANT FIX) ---
df = df.rename(columns={
    'Channel': 'platform',
    'Campaign': 'campaign',
    'Conversions': 'leads',
    'Spend': 'spend',
    'Impressions': 'impressions',
    'Clicks': 'clicks'
})

# --- FIX TYPES ---
numeric_cols = ['spend','impressions','clicks','leads']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- ADD MISSING BUSINESS COLUMNS ---
df['qualified_leads'] = (df['leads'] * 0.4).round()
df['sales'] = (df['leads'] * 0.15).round()
df['revenue'] = df['sales'] * 10000

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
total_sales = filtered_df['sales'].sum()
total_revenue = filtered_df['revenue'].sum()

cpl = total_spend / total_leads if total_leads else 0
cpa = total_spend / total_sales if total_sales else 0
roas = total_revenue / total_spend if total_spend else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Spend", f"₹{total_spend:,.0f}")
c2.metric("Leads", int(total_leads))
c3.metric("Sales", int(total_sales))
c4.metric("Revenue", f"₹{total_revenue:,.0f}")

c5, c6, c7 = st.columns(3)
c5.metric("CPL", f"₹{cpl:,.0f}")
c6.metric("CPA", f"₹{cpa:,.0f}")
c7.metric("ROAS", f"{roas:.2f}")

st.markdown("---")

# --- TABLE ---
st.subheader("📊 Campaign Performance")

table = filtered_df.groupby(['platform','campaign']).agg({
    'spend':'sum',
    'leads':'sum',
    'sales':'sum',
    'revenue':'sum'
}).reset_index()

table['CPL'] = table['spend'] / table['leads']
table['ROAS'] = table['revenue'] / table['spend']

st.dataframe(table.sort_values(by="spend", ascending=False), use_container_width=True)

st.markdown("---")

# --- FUNNEL ---
st.subheader("🔁 Funnel")

funnel_df = pd.DataFrame({
    'Stage': ['Leads','Qualified','Sales'],
    'Count': [
        total_leads,
        filtered_df['qualified_leads'].sum(),
        total_sales
    ]
})

st.bar_chart(funnel_df.set_index('Stage'))

st.markdown("---")

# --- VISUALS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spend by Platform")
    fig1 = px.pie(table, values='spend', names='platform')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Revenue vs Spend")
    fig2 = px.scatter(table, x="spend", y="revenue", size="leads", color="platform")
    st.plotly_chart(fig2, use_container_width=True)