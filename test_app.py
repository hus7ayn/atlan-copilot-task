#!/usr/bin/env python3
"""
Test Streamlit App - Minimal version to debug issues
"""

import streamlit as st
import sys
import os

# Add ai_pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_pipeline'))

st.set_page_config(
    page_title="Test App",
    page_icon="🤖",
    layout="wide"
)

st.title("Test App")

try:
    st.write("Testing imports...")
    
    # Test basic imports
    from simple_tavily_system import get_simple_tavily_system
    st.success("✅ simple_tavily_system import successful")
    
    from file_parser import file_parser
    st.success("✅ file_parser import successful")
    
    # Test sentiment agent
    from sentiment_agent import SentimentAgent
    st.success("✅ SentimentAgent import successful")
    
    # Test tavily integration
    from tavily_rag_integration import TavilyRAGIntegration
    st.success("✅ TavilyRAGIntegration import successful")
    
    st.success("🎉 All imports successful!")
    
except Exception as e:
    st.error(f"❌ Import error: {str(e)}")
    st.error(f"Error type: {type(e).__name__}")
    import traceback
    st.code(traceback.format_exc())
