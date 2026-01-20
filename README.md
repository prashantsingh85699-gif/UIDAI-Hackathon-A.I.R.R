# Aadhaar Inclusion & Risk Radar (A.I.R.R.) 🇮🇳

**Prototype v1.0**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://uidai-hackathon-airr-fnrsde72n5uhxutcebbike.streamlit.app)
**[🔴 Live Demo](https://uidai-hackathon-airr-fnrsde72n5uhxutcebbike.streamlit.app)** 

A.I.R.R. is an AI-powered analytics system designed for UIDAI to monitor Aadhaar ecosystem health. It scores geographical regions on **Inclusion** (saturation, service quality) and **Risk** (fraud, anomalies) to provide actionable insights for administrators.

## 🚀 Key Features
- **Synthetic Data Generator**: Creates realistic mock data for thousands of districts with specific fraud patterns.
- **Scoring Engine**: Computes meaningful inclusion and risk scores based on multi-factor weighted algorithms.
- **Anomaly Detection**: Uses Isolation Forest (ML) and heuristic rules to flag suspicious activity (e.g., bot attacks).
- **Interactive Dashboard**: Streamlit-based UI for exploring data, visualizing risk vs. inclusion, and drilling down into specific districts.
- **Backend API**: FastAPI service to expose processed data and trigger pipeline runs.

## 🛠️ Tech Stack
- **Language**: Python 3.11
- **Frontend**: Streamlit, Plotly
- **Backend**: FastAPI, Uvicorn
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Deployment**: Docker, Docker Compose

## 📦 Installation & Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/aadhaar-airr.git
   cd aadhaar-airr
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate Data** (First Run)
   ```bash
   python scripts/mock_data_gen.py
   python modules/data_pipeline.py
   python modules/scoring_engine.py
   python modules/anomaly_detector.py
   ```

4. **Run the Dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

5. **Run the Backend API** (Optional, for API access)
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

## 🐳 Run with Docker (Recommended)

The easiest way to run the full stack is using Docker Compose.

```bash
docker-compose up --build
```
Access the dashboard at `http://localhost:8501`.

## 📂 Project Structure
```
├── backend/            # FastAPI Backend
├── dashboard/          # Streamlit Frontend
├── data/               # Input/Output Data (Parquet)
├── modules/            # Core Logic (Pipeline, Scoring, Anomaly Detection)
├── scripts/            # Utility Scripts
├── Dockerfile          # Container Definition
└── docker-compose.yml  # Multi-container Setup
```

## 📜 License
This project is a prototype developed for Hackathon purposes.
