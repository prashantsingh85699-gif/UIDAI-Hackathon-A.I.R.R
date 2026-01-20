import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import yaml

# Load config to get synthetic size if available, else default
try:
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
        N_REGIONS = config.get("data", {}).get("synthetic_size", 1000)
except Exception:
    N_REGIONS = 1000

def generate_aadhaar_data(n_regions=1000):
    np.random.seed(42)
    random.seed(42)

    states = ["Maharashtra", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Bihar", "West Bengal", "Rajasthan"]
    
    real_districts = {
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Ghaziabad", "Noida"],
        "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Kalaburagi"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"],
        "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur"]
    }
    
    data = []
    
    for i in range(n_regions):
        state = np.random.choice(states)
        # Pick a real district if available, else generic
        if state in real_districts:
            district_name = np.random.choice(real_districts[state])
            # Append a random number to handle duplicates in specific sub-regions logic if needed, 
            # but for 1000 regions and limited districts, we will have repeats. 
            # Let's make it look unique like "Pune South", "Pune North" or just keep district name and varied sub-districts.
            # To avoid identical rows for same district, we rely on sub_district
            district = district_name
        else:
            district = f"District_{random.randint(1, 30)}"
            
        sub_district = f"Taluk_{random.randint(1, 100)}"
        region_id = f"R{i:05d}"
        
        # Base demographics
        population = int(np.random.lognormal(10, 1)) # Random population size
        if population < 1000: population = 1000
        
        aadhaar_generated = int(population * np.random.uniform(0.7, 0.99))
        missing_aadhaar = population - aadhaar_generated
        
        # Staleness (days since last update for average record)
        # Bimodal distribution: some regions very stale
        if random.random() < 0.2:
            avg_staleness = np.random.uniform(800, 1500) # High staleness
        else:
            avg_staleness = np.random.uniform(100, 600)  # Normal staleness
            
        # Service Quality Metrics
        update_requests = int(aadhaar_generated * np.random.uniform(0.01, 0.15))
        rejected_requests = int(update_requests * np.random.uniform(0.01, 0.30))
        correction_ratio = rejected_requests / update_requests if update_requests > 0 else 0
        avg_processing_time = np.random.uniform(3, 45) # days
        
        # Anomaly / Fraud indicators
        # Spikes in specific update types
        mobile_updates = int(update_requests * np.random.uniform(0.3, 0.7))
        address_updates = int(update_requests * np.random.uniform(0.1, 0.4))
        dob_updates = int(update_requests * np.random.uniform(0.05, 0.2))
        biometric_updates = update_requests - mobile_updates - address_updates - dob_updates
        if biometric_updates < 0: biometric_updates = 0
        
        # Temporal Drift Simulation
        # Simulate staleness drift (change over last month)
        staleness_drift = np.random.normal(0, 10) # positive means getting staler
        if random.random() < 0.1:
            staleness_drift += 50 # Sudden increase in staleness
            
        # Update type entropy input (simplified representation)
        # We will compute actual entropy in pipeline, but here we simulate the raw counts
        
        data.append({
            "region_id": region_id,
            "state": state,
            "district": district,
            "sub_district": sub_district,
            "population": population,
            "aadhaar_generated": aadhaar_generated,
            "avg_staleness_days": avg_staleness,
            "update_requests_total": update_requests,
            "rejected_requests": rejected_requests,
            "avg_processing_time_days": avg_processing_time,
            "mobile_updates": mobile_updates,
            "address_updates": address_updates,
            "dob_updates": dob_updates,
            "biometric_updates": biometric_updates,
            "staleness_drift": staleness_drift,
            "operator_count": random.randint(1, 20),
            "complaints_lodged": int(update_requests * np.random.uniform(0.0, 0.05))
        })
        
    df = pd.DataFrame(data)
    
    # Create outputs directory
    os.makedirs("data/inputs", exist_ok=True)
    output_path = "data/inputs/aadhaar_mock_data.parquet"
    df.to_parquet(output_path, index=False)
    print(f"Generated synthetic data with {n_regions} regions at {output_path}")
    return df

if __name__ == "__main__":
    generate_aadhaar_data(N_REGIONS)
