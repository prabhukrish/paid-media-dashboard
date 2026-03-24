import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. PAGE CONFIG
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

# 2. DEFINE THE FUNCTION FIRST (Crucial to avoid the error)
def standardize_data(df):
    # Clean column names
    df.columns = df.columns.str.strip()
    
    rename_map = {
        'Cost': 'Spend', 
        'Amount Spent (INR)': 'Spend',
        'Amount Spent': 'Spend',
        'Ad Campaign Name': 'Campaign',
        'Campaign Name': 'Campaign',
        'Results': 'Conversions',
        'Link Clicks': 'Clicks'
    }
    df = df.rename(columns=rename_map)
    
    # Ensure numeric columns are actually numbers
    numeric_cols = ['Spend', 'Impressions', 'Clicks', 'Conversions']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

# 3. CUSTOM STYLING
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #007bff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Performance Marketing Dashboard")

# 4. DATA LOADING LOGIC
data_file = "master_data.csv"

if os.path.exists(data_file):
    df_raw = pd.read_csv(data_file)
    df = standardize_data(df_raw)
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Fallback)", type="csv")
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        df = standardize_data(df_raw)
    else:
        st.info("👋 Please upload 'master_data.csv' to your GitHub repo to see the dashboard.")
        st.stop()

# 5. SIDEBAR FILTERS
st.sidebar.header("Filter Options")
search_query = st.sidebar.text_input("Search Campaign Name", "")
unique_channels = df['Channel'].unique() if 'Channel' in df.columns else []
selected_channels = st.sidebar.multiselect("Select Channels", options=unique_channels, default=unique_channels)

# Apply Filters
mask = df['Campaign'].str.contains(search_query, case=False)
if 'Channel' in df.columns:
    mask = mask & (df['Channel'].isin(selected_channels))

filtered_df = df[mask]

# 6. TOP ROW: KPI METRICS (₹ INR)
total_spend = filtered_df['Spend'].sum()
total_clicks = int(filtered_df['Clicks'].sum())
total_conv = filtered_df['Conversions'].sum()
avg_cpa = total_spend / total_conv if total_conv > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Spend", f"₹{total_spend:,.0f}")
m2.metric("Total Clicks", f"{total_clicks:,}")
m3.metric("Conversions", f"{total_conv:,.0f}")
m4.metric("Avg. CPA", f"₹{avg_cpa:,.2f}")

st.markdown("---")

# 7. DETAILED CAMPAIGN TABLE
st.subheader("📊 Detailed Campaign Performance")

# Grouping for Detail
group_cols = ['Channel', 'Campaign'] if 'Channel' in df.columns else ['Campaign']
detail_table = filtered_df.groupby(group_cols).agg({
    'Spend': 'sum',
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()

# Add Metrics
detail_table['CTR %'] = (detail_table['Clicks'] / detail_table['Impressions'] * 100).fillna(0).round(2)
detail_table['CPA'] = (detail_table['Spend'] / detail_table['Conversions']).round(2)

# Format for Display
display_df = detail_table.copy()
display_df['Spend'] = display_df['Spend'].apply(lambda x: f"₹{x:,.0f}")
display_df['CPA'] = display_df['CPA'].apply(lambda x: f"₹{x:,.2f}")

st.dataframe(display_df, use_container_width=True, hide_index=True)