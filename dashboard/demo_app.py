import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# --- Configuration ---
st.set_page_config(
    page_title="UIDAI A.I.R.R. Prototype (Demo)",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading Logic (Integrated from Backend) ---
DATA_PATH = "data/outputs/anomaly_data.parquet"

@st.cache_data(ttl=600)
def load_data():
    """
    Loads data directly from parquet file, bypassing the backend API.
    Handles 'Cold Start' by generating mock data if missing.
    """
    if not os.path.exists(DATA_PATH):
        st.warning("Data not found. Generating mock data for the first time... (This may take a minute)")
        try:
            # Attempt to run generation scripts
            # Assuming we are at project root
            import subprocess
            
            with st.spinner('Generating Mock Data...'):
                subprocess.run([sys.executable, "scripts/mock_data_gen.py"], check=True)
            
            with st.spinner('Running Data Pipeline...'):
                subprocess.run([sys.executable, "modules/data_pipeline.py"], check=True)
                
            with st.spinner('Scoring Regions...'):
                subprocess.run([sys.executable, "modules/scoring_engine.py"], check=True)
                
            with st.spinner('Detecting Anomalies...'):
                subprocess.run([sys.executable, "modules/anomaly_detector.py"], check=True)
                
            st.success("Data Generation Complete!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to generate data: {e}")
            st.info("Ensure you are running this from the project root folder.")
            return None

    try:
        return pd.read_parquet(DATA_PATH)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def get_summary(df):
    if df is None: return None
    return {
        "total_population_covered": int(df['population'].sum()),
        "aadhaar_generated_total": int(df['aadhaar_generated'].sum()),
        "avg_inclusion_score": float(df['inclusion_score'].mean()),
        "avg_risk_score": float(df['risk_score'].mean()),
    }

# --- Sidebar ---
st.sidebar.title("Aadhaar Inclusion Risk Radar")
st.sidebar.caption("Demo Version (Standalone)")

st.sidebar.header("Filters")
# Using a static list for demo speed, or derive from DF
state_filter = st.sidebar.selectbox("Filter by State", ["All", "Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Bihar", "West Bengal", "Rajasthan"])

st.sidebar.divider()
if st.sidebar.button("Regenerate Data (Reset)"):
    st.cache_data.clear()
    # Optional: Delete file to force regeneration?
    # os.remove(DATA_PATH)
    st.rerun()

st.sidebar.markdown("---")


# --- Main Page ---
st.title("Aadhaar Inclusion & Risk Radar")

df = load_data()

if df is not None:
    summary = get_summary(df)
    
    # Top Level Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Population", f"{summary['total_population_covered']:,}")
    kpi2.metric("Aadhaar Generated", f"{summary['aadhaar_generated_total']:,}")
    kpi3.metric("Avg Inclusion Score", f"{summary['avg_inclusion_score']:.1f}%")
    kpi4.metric("Avg Risk Score", f"{summary['avg_risk_score']:.1f}%", delta_color="inverse")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Inclusion Radar", "Risk Radar", "Data Explorer"])

    # Filter Logic
    if state_filter != "All":
        filtered_df = df[df['state'] == state_filter]
    else:
        filtered_df = df

    with tab1:
        st.header("Executive Overview")
        col1, col2 = st.columns([2, 1])
        
        with col1:
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
        col1, col2 = st.columns(2)
        with col1:
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
            fig_risk_dist = px.box(filtered_df, x="state", y="risk_score", title="Risk Score by State")
            st.plotly_chart(fig_risk_dist, use_container_width=True)

    with tab4:
        st.header("Raw Data Explorer")
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("Awaiting data generation...")
