import streamlit as st
import os
import sys

# Add the current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main dashboard app
from dashboard import app

if __name__ == "__main__":
    # This file acts as a root-level entry point that simply invokes the dashboard code.
    # It relies on dashboard/app.py (which we have now ensured is the standalone version).
    pass
