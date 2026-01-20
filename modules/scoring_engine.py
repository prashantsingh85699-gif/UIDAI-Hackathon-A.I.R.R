import pandas as pd
import numpy as np

class ScoringEngine:
    def __init__(self, input_path="data/outputs/processed_data.parquet"):
        self.input_path = input_path
        self.df = None

    def load_data(self):
        try:
            self.df = pd.read_parquet(self.input_path)
            print(f"Scoring Engine: Loaded data with shape: {self.df.shape}")
            return self.df
        except Exception as e:
            print(f"Scoring Engine Error loading data: {e}")
            raise

    def _normalize(self, series, invert=False):
        """Normalizes a series to 0-1 range. If invert is True, 1 is best/lowest."""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(1.0 if invert else 0.0, index=series.index)
        
        normalized = (series - min_val) / (max_val - min_val)
        if invert:
            return 1.0 - normalized
        return normalized

    def calculate_scores(self):
        if self.df is None:
            raise ValueError("Data not loaded")

        # --- Inclusion Score (High is Good) ---
        # Components:
        # 1. Saturation (Higher is better)
        # 2. Avg Processing Time (Lower is better)
        # 3. Rejection/Correction Ratio (Lower is better - indicates smooth process)
        
        norm_saturation = self._normalize(self.df['saturation'], invert=False)
        norm_processing = self._normalize(self.df['avg_processing_time_days'], invert=True)
        norm_correction = self._normalize(self.df['correction_ratio'], invert=True)
        
        # Weighted Sum for Inclusion
        # Weights: Saturation (40%), Processing Speed (30%), Quality/Ease (30%)
        self.df['inclusion_score'] = (
            (norm_saturation * 0.4) + 
            (norm_processing * 0.3) + 
            (norm_correction * 0.3)
        ) * 100
        
        # --- Risk Score (High is Bad/Risky) ---
        # Components:
        # 1. Update Type Entropy (Lower is riskier/anomalous -> Invert normalization to make Low=1)
        #    Wait, standard entropy: High = Random (Good), Low = Deterministic/Spike (Bad/Fraud).
        #    So raw entropy: High is safe, Low is risky.
        #    Normalize(Entropy, invert=True) -> Low entropy becomes close to 1 (High Risk).
        
        # 2. Repeat Update Ratio (Higher is riskier)
        # 3. Updates per Operator (Higher is riskier - overloading/gaming)
        
        norm_entropy_risk = self._normalize(self.df['update_type_entropy'], invert=True) # Low entropy = High Risk
        norm_repeat_risk = self._normalize(self.df['repeat_update_ratio'], invert=False) # High repeat = High Risk
        norm_load_risk = self._normalize(self.df['updates_per_operator'], invert=False) # High load = High Risk
        
        # Weighted Sum for Risk
        # Weights: Entropy (40% - catching specific update dumps), Repeat (30%), Load (30%)
        self.df['risk_score'] = (
            (norm_entropy_risk * 0.4) + 
            (norm_repeat_risk * 0.3) + 
            (norm_load_risk * 0.3)
        ) * 100

        print("Scoring completed.")
        return self.df

    def save_scored_data(self, output_path="data/outputs/scored_data.parquet"):
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cols_to_keep = [
            'region_id', 'state', 'district', 'sub_district', 
            'inclusion_score', 'risk_score',
            'saturation', 'avg_processing_time_days', 'correction_ratio',
            'update_type_entropy', 'repeat_update_ratio', 'updates_per_operator',
            'population', 'aadhaar_generated'
        ]
        # Keep all relevant columns plus scores, maybe drop intermediate raw counts if needed, 
        # but for prototype keep robust set.
        self.df.to_parquet(output_path, index=False)
        print(f"Saved scored data to {output_path}")

if __name__ == "__main__":
    engine = ScoringEngine()
    engine.load_data()
    engine.calculate_scores()
    engine.save_scored_data()
