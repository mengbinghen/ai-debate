"""Main entry point for the AI Debate system."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
from frontend.app import main

if __name__ == "__main__":
    main()
