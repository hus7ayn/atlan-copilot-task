#!/usr/bin/env python3
"""
Atlan Customer Copilot - Minimal Streamlit Application
Ultra-simple version for deployment testing
"""

import streamlit as st
import os
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Atlan Customer Copilot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

def check_api_keys():
    """Check if API keys are configured"""
    claude_key = os.getenv("CLAUDE_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    return bool(claude_key and tavily_key)

# Main app
st.title("🤖 Atlan Customer Copilot")
st.subheader("AI-Powered Customer Support Assistant")

# Check API keys
api_keys_configured = check_api_keys()

if api_keys_configured:
    st.success("✅ API Keys Configured - System Ready!")
    
    # Simple chat interface
    st.header("💬 Chat with AI Assistant")
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Atlan..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Simple demo response
                    response = f"Thanks for your question: '{prompt}'\n\n"
                    response += "I'm your AI assistant powered by Claude and Tavily! "
                    response += "I can help you with Atlan-related questions, documentation search, "
                    response += "and customer support tasks.\n\n"
                    response += "What would you like to know?"
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Features section
    st.header("🚀 Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💬 AI Chat**
        - Real-time responses
        - Context-aware conversations
        - Intelligent routing
        """)
    
    with col2:
        st.markdown("""
        **🔍 Documentation Search**
        - Real-time web search
        - Atlan documentation lookup
        - Knowledge base access
        """)
    
    with col3:
        st.markdown("""
        **📊 Analytics**
        - Sentiment analysis
        - Priority classification
        - Performance metrics
        """)

else:
    # Show setup instructions
    st.warning("⚠️ API Keys Not Configured")
    
    st.markdown("""
    ### 🔧 Setup Required
    
    To enable full functionality, please add your API keys to Streamlit Cloud secrets:
    
    **In Streamlit Cloud Secrets:**
    ```toml
    CLAUDE_API_KEY = "your_claude_api_key"
    TAVILY_API_KEY = "your_tavily_api_key"
    ```
    
    ### 🎯 What You'll Get
    
    Once configured, your AI assistant will provide:
    - **Intelligent Responses** using Claude AI
    - **Real-time Search** via Tavily integration  
    - **File Processing** for support tickets
    - **Analytics Dashboard** with insights
    
    ### 📞 Support
    
    Need help? The AI assistant can help with:
    - Atlan platform questions
    - Data governance guidance
    - Technical troubleshooting
    - Best practices advice
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🤖 Atlan Customer Copilot | Powered by Claude AI & Tavily Search
</div>
""", unsafe_allow_html=True)
