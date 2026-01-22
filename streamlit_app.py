import streamlit as st
import os
import sys
import runpy

if __name__ == "__main__":
    # Use runpy to execute the dashboard script in the current process.
    # This ensures that Streamlit magic and re-runs work correctly, 
    # avoiding issues with module caching that occur when just 'importing' the app.
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "dashboard", "app.py")
    
    runpy.run_path(app_path)
