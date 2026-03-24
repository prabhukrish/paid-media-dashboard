import pandas as pd

def clean_google(file_path):
    df = pd.read_csv(file_path)
    # Google uses 'Cost', 'Campaign', 'Clicks', etc.
    df = df[['Campaign', 'Cost', 'Impressions', 'Clicks', 'Conversions']].copy()
    df.columns = ['Campaign', 'Spend', 'Impressions', 'Clicks', 'Conversions']
    df['Channel'] = 'Google'
    return df

def clean_meta(file_path):
    df = pd.read_csv(file_path)
    # Meta often uses 'Campaign Name', 'Amount Spent (USD)', 'Results'
    # Adjust these strings if your Meta export headers are different
    df = df[['Campaign Name', 'Amount Spent (USD)', 'Impressions', 'Link Clicks', 'Results']].copy()
    df.columns = ['Campaign', 'Spend', 'Impressions', 'Clicks', 'Conversions']
    df['Channel'] = 'Meta'
    return df

# --- RUN THE MERGE ---
try:
    google_df = clean_google('google_export.csv')
    meta_df = clean_meta('meta_export.csv')

    master_df = pd.concat([google_df, meta_df], ignore_index=True)
    master_df.to_csv('master_data.csv', index=False)
    print("✅ Success! 'master_data.csv' created.")
except FileNotFoundError as e:
    print(f"❌ Error: Could not find the file. Make sure names match. {e}")