import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self, input_path="data/outputs/scored_data.parquet"):
        self.input_path = input_path
        self.df = None

    def load_data(self):
        try:
            self.df = pd.read_parquet(self.input_path)
            print(f"AnomalyDetector: Loaded data with shape: {self.df.shape}")
            return self.df
        except Exception as e:
            print(f"AnomalyDetector: Error loading data: {e}")
            raise

    def detect_anomalies(self):
        if self.df is None:
            raise ValueError("Data not loaded")

        # Features for anomaly detection
        # We focus on the 'risk' related metrics + raw heavy hitters
        features = [
            'update_type_entropy',
            'repeat_update_ratio',
            'updates_per_operator',
            'avg_processing_time_days',
            'rejected_requests'
        ]
        
        # Prepare data
        X = self.df[features].fillna(0)
        
        # --- Method 1: Isolation Forest (Global Anomalies) ---
        print("Running Isolation Forest...")
        iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.df['anomaly_score_if'] = iso_forest.fit_predict(X)
        self.df['is_anomaly_if'] = self.df['anomaly_score_if'] == -1
        
        # --- Method 2: Statistical Heuristics (Domain Specific) ---
        # Rule: Low Entropy AND High Load -> Bot/Script Attack?
        # Rule: High Rejection AND High Processing Time -> Inefficiency/Grievance
        
        # Define Thresholds (e.g., top 98th percentile is anomalous)
        high_load_thresh = self.df['updates_per_operator'].quantile(0.98)
        low_entropy_thresh = self.df['update_type_entropy'].quantile(0.02)
        
        self.df['is_anomaly_rule_bot'] = (
            (self.df['updates_per_operator'] > high_load_thresh) & 
            (self.df['update_type_entropy'] < low_entropy_thresh)
        )
        
        # Combine
        self.df['is_anomaly'] = self.df['is_anomaly_if'] | self.df['is_anomaly_rule_bot']
        
        # Assign Reasons
        self.df['anomaly_reason'] = "Normal"
        self.df.loc[self.df['is_anomaly_if'], 'anomaly_reason'] = "Statistical Outlier"
        self.df.loc[self.df['is_anomaly_rule_bot'], 'anomaly_reason'] = "High Load + Low Entropy (Bot?)"
        
        count = self.df['is_anomaly'].sum()
        print(f"Detected {count} anomalies out of {len(self.df)} regions.")
        
        return self.df

    def save_anomalies(self, output_path="data/outputs/anomaly_data.parquet"):
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_parquet(output_path, index=False)
        print(f"Saved anomaly data to {output_path}")

if __name__ == "__main__":
    detector = AnomalyDetector()
    detector.load_data()
    detector.detect_anomalies()
    detector.save_anomalies()
