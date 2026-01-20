import pandas as pd
import os

def inspect_data():
    path = "data/outputs/anomaly_data.parquet"
    if not os.path.exists(path):
        print(f"File not found: {path} - Please run the pipeline first.")
        return

    df = pd.read_parquet(path)
    
    print("--- DATASET SUMMARY ---")
    print(f"Total Regions: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n--- SCORES (Averages) ---")
    print(f"Avg Inclusion Score: {df['inclusion_score'].mean():.2f}")
    print(f"Avg Risk Score:      {df['risk_score'].mean():.2f}")
    
    print("\n--- ANOMALY DETECTION RESULTS ---")
    anomalies = df[df['is_anomaly'] == True]
    print(f"Total Anomalies Detected: {len(anomalies)} ({len(anomalies)/len(df)*100:.2f}%)")
    
    if len(anomalies) > 0:
        print("\n--- TOP 5 RISKY REGIONS (ANOMALIES) ---")
        top_risky = anomalies.sort_values(by="risk_score", ascending=False).head(5)
        # Select specific columns to display
        display_cols = ['district', 'state', 'risk_score', 'inclusion_score', 'anomaly_reason', 'update_type_entropy']
        print(top_risky[display_cols].to_string(index=False))
    else:
        print("No anomalies found (or threshold too loose).")

if __name__ == "__main__":
    inspect_data()
