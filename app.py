"""HuggingFace Spaces Entry Point - Streamlit Frontend"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main Streamlit app
from frontend.streamlit_app import *
