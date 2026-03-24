import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

# --- DATA LOADING (AUTOMATIC & BUG-FREE) ---

# 1. Define the file path
data_file = "master_data.csv"

# 2. Check if the file exists on GitHub
if os.path.exists(data_file):
    # Load the data first
    df_raw = pd.read_csv(data_file)
    # Then standardize it
    df = standardize_data(df_raw)
else:
    # Fallback to manual upload if CSV is missing from GitHub
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Fallback)", type="csv")
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        df = standardize_data(df_raw)
    else:
        st.info("👋 Welcome! Please upload 'master_data.csv' to your GitHub repo to see the dashboard automatically.")
        st.stop()

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #007bff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def standardize_data(df):
    # Clean column names (strip spaces and lowercase for easier matching)
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
    st.warning("⚠️ No data found. Please upload a CSV to the sidebar or add 'master_data.csv' to GitHub.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")
search_query = st.sidebar.text_input("Search Campaign Name", "")
selected_channels = st.sidebar.multiselect("Select Channels", options=df['Channel'].unique(), default=df['Channel'].unique())

# Apply Filters
filtered_df = df[(df['Channel'].isin(selected_channels)) & 
                 (df['Campaign'].str.contains(search_query, case=False))]

# --- TOP ROW: KPI METRICS (₹ INR) ---
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

# --- DETAILED CAMPAIGN TABLE ---
st.subheader("📊 Detailed Campaign Performance")

# Grouping for Detail
detail_table = filtered_df.groupby(['Channel', 'Campaign']).agg({
    'Spend': 'sum',
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()

# Calculations
detail_table['CTR %'] = (detail_table['Clicks'] / detail_table['Impressions'] * 100).fillna(0).round(2)
detail_table['Conv. Rate %'] = (detail_table['Conversions'] / detail_table['Clicks'] * 100).fillna(0).round(2)
detail_table['CPA'] = (detail_table['Spend'] / detail_table['Conversions']).round(2)

# Formatting for management view
display_df = detail_table.copy()
display_df['Spend'] = display_df['Spend'].apply(lambda x: f"₹{x:,.0f}")
display_df['CPA'] = display_df['CPA'].apply(lambda x: f"₹{x:,.2f}")

st.dataframe(display_df, use_container_width=True, hide_index=True)

# --- VISUALS ---
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Spend by Channel")
    fig_pie = px.pie(detail_table, values='Spend', names='Channel', hole=0.5, 
                     color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    st.subheader("Conversions vs. Spend")
    fig_scatter = px.scatter(detail_table, x="Spend", y="Conversions", size="Clicks", 
                             color="Channel", hover_name="Campaign",
                             labels={"Spend": "Spend (₹)"})
    st.plotly_chart(fig_scatter, use_container_width=True)