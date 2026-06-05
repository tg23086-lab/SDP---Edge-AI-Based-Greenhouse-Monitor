import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="StemCube Dashboard", layout="wide")
st.title("🚀 StemCube Real-Time Air Quality Monitor")

# ==============================================================================
# 1. GOOGLE SHEET URL
# ==============================================================================
RAW_URL = "https://docs.google.com/spreadsheets/d/17LZoyqljzT9sqNZwSPNePSEMYIWPG7gdFKuEZHI-2Bo/edit?gid=0#gid=0"

def get_clean_csv_url(url):
    if "/edit" in url:
        base = url.split("/edit")[0]
        return f"{base}/gviz/tq?tqx=out:csv&sheet=Deployment"
    return url

CSV_URL = get_clean_csv_url(RAW_URL)

# --- TRUE REAL-TIME AUTO REFRESH TRIGGER ---
# This silently refreshes the data frame component every 3 seconds in the background.
# The user will see new data pop up instantly as soon as the Pico uploads it!
st_autorefresh(interval=3000, key="datarefresh")

def fetch_data(url):
    # Standard read with a query bypass string to beat any aggressive browser-side caching
    return pd.read_csv(f"{url}&nocache={pd.Timestamp.now().timestamp()}")

try:
    df = fetch_data(CSV_URL)
    
    if not df.empty:
        # Standardize column headers
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        latest = df.iloc[-1]
        
        st.caption("🟢 Live Tracking Active (System checks Google Sheets every 3s)")
        st.subheader(f"Last Updated from Pico: {latest.get('timestamp', 'N/A')}")
        
        # --- DASHBOARD LAYOUT ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("eCO2 Level", f"{latest.get('eco2_ppm', 0)} ppm")
        col2.metric("TVOC Level", f"{latest.get('tvoc_ppb', 0)} ppb")
        col3.metric("Temperature", f"{latest.get('temperature_c', 0.0)} °C")
        
        # Color coding the status via markdown for visual flair during presentation
        cond_str = str(latest.get('condition', 'N/A')).upper()
        if "DANGER" in cond_str:
            st.error(f"🚨 CRITICAL SYSTEM STATUS: {cond_str}")
        elif "ALERT" in cond_str:
            st.warning(f"⚠️ ATTENTION REQUIRED: {cond_str}")
        else:
            col4.metric("Current Condition", cond_str)
        
        st.divider()
        
        # Interactive Analytics Visualizations
        st.subheader("📈 Air Quality Trends")
        st.line_chart(df, x="timestamp", y=["eco2_ppm", "tvoc_ppb"])
        
        st.subheader("🌡️ Environment Metrics")
        st.line_chart(df, x="timestamp", y=["temperature_c", "humidity_pct"])
        
        # Raw log data grid
        st.subheader("📋 Raw Data Log")
        st.dataframe(df, use_container_width=True)
        
    else:
        st.warning("Connected to the sheet, but no data rows were found.")

except Exception as e:
    st.error(f"Could not connect to Google Sheets: {e}")