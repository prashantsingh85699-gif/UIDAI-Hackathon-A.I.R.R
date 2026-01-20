import requests
import time

def check_service(name, url):
    print(f"Checking {name} at {url}...")
    try:
        response = requests.get(url, timeout=2)
        print(f"✅ {name} is reachable! Status Code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is NOT reachable. Connection Refused.")
        return False
    except Exception as e:
        print(f"⚠️ {name} Error: {e}")
        return False

# Check Backend
backend_ok = check_service("Backend API", "http://127.0.0.1:8000/health")

# Check Dashboard (Streamlit returns 200 on healthz usually, but main page is fine too)
dashboard_ok = check_service("Streamlit Dashboard", "http://127.0.0.1:8501/_stcore/health")

if not dashboard_ok:
     # try main page if health check fails (older streamlit versions)
     dashboard_ok = check_service("Streamlit Dashboard (Main)", "http://127.0.0.1:8501")

if backend_ok and dashboard_ok:
    print("\nBOTH SERVICES ARE RUNNING CORRECTLY.")
else:
    print("\nONE OR MORE SERVICES FAILED.")
