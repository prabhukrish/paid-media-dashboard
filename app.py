import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

# Custom CSS to make it look cleaner
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    </style>
    """, unsafe_index=True)

def standardize_data(df):
    rename_map = {
        'Cost': 'Spend', 
        'Amount Spent (INR)': 'Spend',
        'Amount Spent (USD)': 'Spend', # In case you haven't converted yet
        'Ad Campaign Name': 'Campaign',
        'Campaign Name': 'Campaign',
        'Results': 'Conversions',
        'Link Clicks': 'Clicks'
    }
    df = df.rename(columns=rename_map)
    # Ensure numeric columns are actually numbers
    cols = ['Spend', 'Impressions', 'Clicks', 'Conversions']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

st.title("🎯 Performance Marketing Dashboard")

# --- DATA LOADING ---
uploaded_file = st.sidebar.file_uploader("Upload New Data", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = standardize_data(df)
elif os.path.exists("master_data.csv"):
    df = pd.read_csv("master_data.csv")
    df = standardize_data(df)
else:
    st.warning("⚠️ No data found. Please upload a CSV to the sidebar.")
    st.stop()

# --- CALCULATIONS ---
total_spend = df['Spend'].sum()
total_clicks = int(df['Clicks'].sum())
total_conv = df['Conversions'].sum()
avg_cpa = total_spend / total_conv if total_conv > 0 else 0
avg_ctr = (total_clicks / df['Impressions'].sum() * 100) if df['Impressions'].sum() > 0 else 0

# --- TOP ROW: KPI METRICS (RUPEES) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Spend", f"₹{total_spend:,.0f}")
m2.metric("Total Clicks", f"{total_clicks:,}")
m3.metric("Conversions", f"{total_conv:,.0f}")
m4.metric("Avg. CPA", f"₹{avg_cpa:,.2f}")

st.markdown("---")

# --- DETAILED CAMPAIGN TABLE ---
st.subheader("📊 Detailed Campaign Performance")

# Filtering by Channel in Sidebar
selected_channels = st.sidebar.multiselect("Select Channels", options=df['Channel'].unique(), default=df['Channel'].unique())
filtered_df = df[df['Channel'].isin(selected_channels)]

# Group by Channel AND Campaign to show detail
detail_table = filtered_df.groupby(['Channel', 'Campaign']).agg({
    'Spend': 'sum',
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()

# Add calculated columns for detail
detail_table['CTR %'] = (detail_table['Clicks'] / detail_table['Impressions'] * 100).round(2)
detail_table['CPA'] = (detail_table['Spend'] / detail_table['Conversions']).round(2)

# Format for display
formatted_table = detail_table.copy()
formatted_table['Spend'] = formatted_table['Spend'].apply(lambda x: f"₹{x:,.0f}")
formatted_table['CPA'] = formatted_table['CPA'].apply(lambda x: f"₹{x:,.2f}")

st.dataframe(formatted_table, use_container_width=True, hide_index=True)

# --- VISUALS ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("Spend Distribution")
    fig_pie = px.pie(detail_table, values='Spend', names='Channel', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("Campaign Cost vs. Conversions")
    fig_scatter = px.scatter(detail_table, x="Spend", y="Conversions", size="Clicks", color="Channel", hover_name="Campaign")
    st.plotly_chart(fig_scatter, use_container_width=True)