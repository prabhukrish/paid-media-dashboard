\import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

# --- 2. DATA STANDARDIZATION FUNCTION ---
def standardize_data(df):
    # Clean column names (remove hidden spaces)
    df.columns = df.columns.str.strip()
    
    # Mapping various platform names to a single standard
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
    
    # Ensure Channel and Campaign are strings
    if 'Channel' in df.columns:
        df['Channel'] = df['Channel'].astype(str)
    if 'Campaign' in df.columns:
        df['Campaign'] = df['Campaign'].astype(str)
        
    return df

# --- 3. CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 32px; color: #007bff; font-weight: bold; }
    /* Style the dataframe to look more professional */
    [data-testid="stTable"] { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Performance Marketing Dashboard")

# --- 4. DATA LOADING LOGIC ---
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
        st.info("👋 Please upload 'master_data.csv' to your GitHub repo or use the sidebar to see the dashboard.")
        st.stop()

# --- 5. SIDEBAR FILTERS ---
st.sidebar.header("Filter Options")

# A. Search Bar
search_query = st.sidebar.text_input("Search Campaign Name", "")

# B. Channel Filter
unique_channels = df['Channel'].unique().tolist() if 'Channel' in df.columns else []
selected_channels = st.sidebar.multiselect("Select Channels", options=unique_channels, default=unique_channels)

# C. Campaign Picker (The Select/Deselect Feature)
# First filter the list by selected channels
available_campaigns = df[df['Channel'].isin(selected_channels)]['Campaign'].unique().tolist()

selected_campaigns = st.sidebar.multiselect(