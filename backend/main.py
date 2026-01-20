from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import subprocess
import asyncio
from typing import List, Optional

app = FastAPI(title="Aadhaar A.I.R.R. API", version="0.1.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "data/outputs/anomaly_data.parquet"

def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    try:
        return pd.read_parquet(DATA_PATH)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Aadhaar A.I.R.R. Backend"}

@app.get("/api/summary")
def get_summary():
    df = load_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not available. Run pipeline first.")
    
    summary = {
        "total_regions": len(df),
        "total_population_covered": int(df['population'].sum()),
        "aadhaar_generated_total": int(df['aadhaar_generated'].sum()),
        "avg_inclusion_score": float(df['inclusion_score'].mean()),
        "avg_risk_score": float(df['risk_score'].mean()),
        "total_anomalies": int(df['is_anomaly'].sum()),
        "high_risk_regions": int(len(df[df['risk_score'] > 80]))
    }
    return summary

@app.get("/api/regions")
def get_regions(
    state: Optional[str] = None, 
    min_risk: float = 0.0, 
    is_anomaly: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    df = load_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not available.")
        
    # Filtering
    if state:
        df = df[df['state'] == state]
    
    if min_risk > 0:
        df = df[df['risk_score'] >= min_risk]
        
    if is_anomaly is not None:
        df = df[df['is_anomaly'] == is_anomaly]
        
    # Pagination
    total_count = len(df)
    df_paginated = df.iloc[offset : offset + limit]
    
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "data": df_paginated.to_dict(orient="records")
    }

@app.get("/api/anomalies/top")
def get_top_anomalies(limit: int = 10):
    df = load_data()
    if df is None:
        raise HTTPException(status_code=404, detail="Data not available.")
    
    # Sort by risk score descending
    anomalies = df[df['is_anomaly'] == True].sort_values(by='risk_score', ascending=False).head(limit)
    
    return anomalies.to_dict(orient="records")

@app.post("/api/pipeline/run")
async def run_pipeline():
    """
    Triggers the data pipeline scripts asynchronously.
    """
    try:
        # We'll run them sequentially for simplicity in this prototype
        commands = [
            "python scripts/mock_data_gen.py", 
            "python modules/data_pipeline.py", 
            "python modules/scoring_engine.py", 
            "python modules/anomaly_detector.py"
        ]
        
        # Non-blocking run (fire and forget for this simple prototype, 
        # or wait if we want to return success only after done. 
        # Given the speed, we can wait.)
        
        for cmd in commands:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise Exception(f"Command {cmd} failed: {stderr.decode()}")
                
        return {"status": "success", "message": "Pipeline execution completed."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
