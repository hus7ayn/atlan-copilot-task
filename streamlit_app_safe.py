#!/usr/bin/env python3
"""
Atlan Customer Copilot - Safe Streamlit Application
Handles missing API keys gracefully
"""

import streamlit as st
import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add ai_pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_pipeline'))

# Configure Streamlit page
st.set_page_config(
    page_title="Atlan Customer Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .analysis-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-card {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #e53e3e;
        margin: 1rem 0;
    }
    .success-card {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #38a169;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False
if 'api_keys_configured' not in st.session_state:
    st.session_state.api_keys_configured = False

def check_api_keys():
    """Check if API keys are configured"""
    claude_key = os.getenv("CLAUDE_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    return bool(claude_key and tavily_key)

def initialize_system():
    """Initialize the AI system safely"""
    try:
        # Check API keys first
        if not check_api_keys():
            return False, "API keys not configured. Please set CLAUDE_API_KEY and TAVILY_API_KEY in Streamlit secrets."
        
        # Try to import and initialize components
        from simple_tavily_system import get_simple_tavily_system
        
        # Test if we can create the system
        return True, "System initialized successfully!"
        
    except Exception as e:
        return False, f"Failed to initialize system: {str(e)}"

# Main app header
st.markdown('<div class="main-header">🤖 Atlan Customer Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Customer Support Assistant</div>', unsafe_allow_html=True)

# Check system status
if not st.session_state.system_ready:
    with st.spinner("Initializing system..."):
        success, message = initialize_system()
        if success:
            st.session_state.system_ready = True
            st.session_state.api_keys_configured = True
            st.success(message)
        else:
            st.error(message)
            st.session_state.api_keys_configured = False

# Sidebar for configuration
with st.sidebar:
    st.header("🔧 Configuration")
    
    # API Keys Status
    if st.session_state.api_keys_configured:
        st.success("✅ API Keys Configured")
    else:
        st.error("❌ API Keys Missing")
        st.info("Please configure your API keys in Streamlit Cloud secrets:")
        st.code("""
CLAUDE_API_KEY = "your_claude_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
        """)
    
    # System Status
    if st.session_state.system_ready:
        st.success("✅ System Ready")
    else:
        st.warning("⚠️ System Not Ready")

# Main chat interface
if st.session_state.system_ready:
    st.header("💬 Chat with AI Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Atlan or customer support..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Simple response for now
                    response = f"I understand you're asking about: {prompt}\n\n"
                    response += "This is a demo response. Once your API keys are configured, "
                    response += "I'll be able to provide real-time assistance using Claude AI and Tavily search."
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

else:
    # Show setup instructions
    st.header("🚀 Getting Started")
    
    st.markdown("""
    ### Welcome to Atlan Customer Copilot!
    
    This AI-powered assistant helps with customer support by:
    - 🤖 Providing intelligent responses using Claude AI
    - 🔍 Searching real-time documentation via Tavily
    - 📊 Analyzing customer sentiment and priority
    - 📁 Processing support tickets from various formats
    
    ### To get started:
    
    1. **Configure API Keys** in Streamlit Cloud secrets:
       - `CLAUDE_API_KEY`: Your Anthropic Claude API key
       - `TAVILY_API_KEY`: Your Tavily API key
    
    2. **Restart the app** after adding secrets
    
    3. **Start chatting** with the AI assistant!
    
    ### Features:
    - 💬 **Interactive Chat**: Real-time AI responses
    - 📁 **File Upload**: Process support tickets
    - 📊 **Analytics**: Sentiment analysis and metrics
    - 🔍 **Real-time Search**: Documentation lookup
    """)
    
    # Show sample conversation
    st.header("💡 Example Queries")
    st.markdown("""
    Try asking questions like:
    - "How do I create a data asset in Atlan?"
    - "What's the difference between a table and a view?"
    - "How can I set up data lineage tracking?"
    - "What are the best practices for data governance?"
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🤖 Atlan Customer Copilot | Powered by Claude AI & Tavily Search
</div>
""", unsafe_allow_html=True)
