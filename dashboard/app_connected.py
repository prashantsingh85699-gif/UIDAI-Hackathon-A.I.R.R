import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import time

# --- Configuration ---
st.set_page_config(
    page_title="UIDAI A.I.R.R. Prototype",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
import os

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000/api")

# --- Helper Functions ---
@st.cache_data(ttl=60)
def fetch_summary():
    try:
        response = requests.get(f"{API_URL}/summary")
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

@st.cache_data(ttl=60)
def fetch_data(limit=1000):
    try:
        # Fetching a larger chunk for client-side viz in prototype
        response = requests.get(f"{API_URL}/regions?limit={limit}")
        if response.status_code == 200:
            data = response.json().get("data", [])
            return pd.DataFrame(data)
    except:
        return pd.DataFrame()
    return pd.DataFrame()

def trigger_pipeline():
    try:
        requests.post(f"{API_URL}/pipeline/run")
        st.toast("Pipeline started! Data refreshing...", icon="🔄")
        time.sleep(2)
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Failed to trigger pipeline: {e}")

# --- Sidebar ---
st.sidebar.title("Aadhaar Inclusion Risk Radar")

st.sidebar.header("Filters")
selected_state = st.sidebar.selectbox("Filter by State", ["All"] + ["Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Bihar", "West Bengal", "Rajasthan"]) # Hardcoded for prototype speed, ideally fetch from API

st.sidebar.divider()
if st.sidebar.button("Run Data Pipeline"):
    trigger_pipeline()

st.sidebar.markdown("---")


# --- Main Page ---
st.title("Aadhaar Inclusion & Risk Radar")

summary = fetch_summary()
df = fetch_data(limit=2000)

if summary:
    # Top Level Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Population", f"{summary['total_population_covered']:,}")
    kpi2.metric("Aadhaar Generated", f"{summary['aadhaar_generated_total']:,}")
    kpi3.metric("Avg Inclusion Score", f"{summary['avg_inclusion_score']:.1f}%")
    kpi4.metric("Avg Risk Score", f"{summary['avg_risk_score']:.1f}%", delta_color="inverse")
else:
    st.warning("Backend API not reachable. Ensure `backend/main.py` is running.")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Inclusion Radar", "Risk Radar", "Data Explorer"])

with tab1:
    st.header("Executive Overview")
    
    # Filter DF if State selected
    if selected_state != "All":
        filtered_df = df[df['state'] == selected_state]
    else:
        filtered_df = df
        
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bubble Chart: Inclusion vs Risk
        fig = px.scatter(
            filtered_df, 
            x="inclusion_score", 
            y="risk_score", 
            size="population", 
            color="is_anomaly",
            hover_name="district",
            title="District Performance Matrix (Inclusion vs Risk)",
            labels={"inclusion_score": "Inclusion Score (High Good)", "risk_score": "Risk Score (Low Good)"},
            color_discrete_map={False: "#636EFA", True: "#EF553B"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Anomaly Distribution
        st.subheader("Top Anomalies")
        anomalies = filtered_df[filtered_df['is_anomaly'] == True].sort_values(by="risk_score", ascending=False).head(10)
        st.dataframe(
            anomalies[['district', 'risk_score', 'anomaly_reason']], 
            hide_index=True,
            use_container_width=True
        )

with tab2:
    st.header("Inclusion Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        fig_sat = px.histogram(filtered_df, x="saturation", nbins=20, title="Saturation Distribution")
        st.plotly_chart(fig_sat, use_container_width=True)
        
    with col2:
        fig_qual = px.scatter(
            filtered_df, 
            x="avg_processing_time_days", 
            y="correction_ratio", 
            color="state", 
            title="Service Quality: Processing Time vs Corrections"
        )
        st.plotly_chart(fig_qual, use_container_width=True)

with tab3:
    st.header("Risk & Fraud Detection")
    st.markdown("Analyzing anomalous patterns in update requests.")
    
    col1, col2 = st.columns(2)
    with col1:
        # Entropy vs Load (The flagging rule)
        fig_risk = px.scatter(
            filtered_df,
            x="update_type_entropy",
            y="updates_per_operator",
            color="is_anomaly",
            title="Entropy vs. Operator Load (Bot Detection)",
            hover_data=["district"]
        )
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col2:
        st.subheader("Risk Score Distribution")
        fig_risk_dist = px.box(filtered_df, x="state", y="risk_score", title="Risk Score by State")
        st.plotly_chart(fig_risk_dist, use_container_width=True)

with tab4:
    st.header("Raw Data Explorer")
    st.dataframe(filtered_df, use_container_width=True)
