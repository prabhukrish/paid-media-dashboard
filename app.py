import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

# Standardizing Function (The part that had the error)
def standardize_data(df):
    # Mapping various platform names to a single standard
    rename_map = {
        'Cost': 'Spend', 
        'Amount Spent (USD)': 'Spend',
        'Ad Campaign Name': 'Campaign',
        'Campaign Name': 'Campaign',
        'Results': 'Conversions',
        'Link Clicks': 'Clicks'
    }
    return df.rename(columns=rename_map)

st.title("🎯 Paid Campaign Performance")

# --- DATA LOADING LOGIC ---
uploaded_file = st.sidebar.file_uploader("Upload New Data", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df = standardize_data(df)
elif os.path.exists("master_data.csv"):
    df = pd.read_csv("master_data.csv")
    # No need to standardize if the merger script already did it, 
    # but safe to keep here just in case.
    df = standardize_data(df)
else:
    st.warning("⚠️ No data found. Please upload a CSV to the sidebar.")
    st.stop()

# --- DASHBOARD VISUALS ---
# 1. Top Row KPIs
m1, m2, m3, m4 = st.columns(4)
total_spend = df['Spend'].sum()
total_conv = df['Conversions'].sum()

m1.metric("Total Spend", f"${total_spend:,.2f}")
m2.metric("Total Clicks", f"{df['Clicks'].sum():,}")
m3.metric("Conversions", f"{total_conv:,}")
m4.metric("CPA", f"${(total_spend/total_conv):.2f}" if total_conv > 0 else "$0")

st.markdown("---")

# 2. Main Table & Chart
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Performance by Channel")
    summary = df.groupby('Channel').sum(numeric_only=True).reset_index()
    st.dataframe(summary, use_container_width=True)

with col2:
    st.subheader("Budget Split")
    fig = px.pie(summary, values='Spend', names='Channel', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)