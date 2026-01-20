import pandas as pd
import numpy as np
from scipy.stats import entropy

class DataPipeline:
    def __init__(self, input_path="data/inputs/aadhaar_mock_data.parquet"):
        self.input_path = input_path
        self.df = None
        
    def load_data(self):
        """Loads data from parquet file."""
        try:
            self.df = pd.read_parquet(self.input_path)
            print(f"Loaded data with shape: {self.df.shape}")
            return self.df
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def preprocess(self):
        """Basic cleaning and preprocessing."""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        # Fill missing values
        self.df.fillna(0, inplace=True)
        
        # Ensure non-negative
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        self.df[numerical_cols] = self.df[numerical_cols].clip(lower=0)
        
        return self.df

    def _calculate_entropy(self, row):
        """Calculates Shannon entropy of update types."""
        counts = [
            row['mobile_updates'],
            row['address_updates'],
            row['dob_updates'],
            row['biometric_updates']
        ]
        total = sum(counts)
        if total == 0:
            return 0
        probs = [c / total for c in counts]
        return entropy(probs, base=2)

    def feature_engineering(self):
        """Creates derived features for scoring."""
        if self.df is None:
            raise ValueError("Data not loaded.")
            
        # 1. Update Type Entropy
        # Low entropy -> dominance of one update type (potential fraud/gaming)
        self.df['update_type_entropy'] = self.df.apply(self._calculate_entropy, axis=1)
        
        # 2. Correction Ratio (Quality Metric)
        self.df['correction_ratio'] = self.df['rejected_requests'] / self.df['update_requests_total'].replace(0, 1)
        
        # 3. Repeat Update Ratio Proxy (Simulated as function of rejection for now as we lack individual tx data)
        # In real scenario, this would come from tx level logs
        self.df['repeat_update_ratio'] = (self.df['rejected_requests'] * 1.5) / self.df['update_requests_total'].replace(0, 1)
        self.df['repeat_update_ratio'] = self.df['repeat_update_ratio'].clip(upper=1.0)
        
        # 4. Saturation
        self.df['saturation'] = self.df['aadhaar_generated'] / self.df['population'].replace(0, 1)
        
        # 5. Anomaly Susceptibility (heuristic)
        # High volume + low operators = suspicious
        self.df['updates_per_operator'] = self.df['update_requests_total'] / self.df['operator_count'].replace(0, 1)
        
        print("Feature engineering completed.")
        return self.df
        
    def save_processed(self, output_path="data/outputs/processed_data.parquet"):
        """Saves processed dataframe."""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_parquet(output_path, index=False)
        print(f"Saved processed data to {output_path}")

if __name__ == "__main__":
    # Test run
    pipeline = DataPipeline()
    pipeline.load_data()
    pipeline.preprocess()
    pipeline.feature_engineering()
    pipeline.save_processed()
