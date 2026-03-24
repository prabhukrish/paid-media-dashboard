import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Paid Media Dashboard", layout="wide")

st.title("🎯 Paid Campaign Performance")
st.markdown("---")

# 1. SIDEBAR - File Upload & Filters
st.sidebar.header("Data Control")
uploaded_file = st.sidebar.file_uploader("Upload your Campaign CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Simple Sidebar Filters
    channels = st.sidebar.multiselect("Filter by Channel", options=df['Channel'].unique(), default=df['Channel'].unique())
    campaigns = st.sidebar.multiselect("Filter by Campaign", options=df['Campaign'].unique(), default=df['Campaign'].unique())
    
    # Filtered Dataframe
    mask = (df['Channel'].isin(channels)) & (df['Campaign'].isin(campaigns))
    filtered_df = df[mask]

    # 2. TOP ROW - KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    total_spend = filtered_df['Spend'].sum()
    total_conversions = filtered_df['Conversions'].sum()
    avg_cpa = total_spend / total_conversions if total_conversions > 0 else 0
    
    m1.metric("Total Spend", f"${total_spend:,.2f}")
    m2.metric("Impressions", f"{filtered_df['Impressions'].sum():,}")
    m3.metric("Conversions", f"{total_conversions:,}")
    m4.metric("Avg. CPA", f"${avg_cpa:.2f}")

    st.markdown("---")

    # 3. MIDDLE ROW - Table & Chart
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Channel Breakdown")
        # Grouping data like your reference image
        summary = filtered_df.groupby('Channel').agg({
            'Spend': 'sum',
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Conversions': 'sum'
        }).reset_index()
        st.dataframe(summary, use_container_width=True)

    with col_right:
        st.subheader("Spend Distribution")
        fig = px.pie(summary, values='Spend', names='Channel', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload a CSV file to begin. Ensure columns are: Channel, Campaign, Spend, Impressions, Clicks, Conversions")