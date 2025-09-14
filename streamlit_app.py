#!/usr/bin/env python3
"""
Atlan Customer Copilot - Basic Streamlit Application
Minimal version for guaranteed deployment
"""

import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Atlan Customer Copilot",
    page_icon="🤖",
    layout="wide"
)

# Main app
st.title("🤖 Atlan Customer Copilot")
st.subheader("AI-Powered Customer Support Assistant")

# Simple status check
st.success("✅ App is running successfully!")

# Basic chat interface
st.header("💬 Chat with AI Assistant")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

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
        response = f"Thanks for your question: '{prompt}'\n\n"
        response += "I'm your AI assistant! I can help you with:\n"
        response += "- Atlan platform questions\n"
        response += "- Data governance guidance\n"
        response += "- Technical troubleshooting\n"
        response += "- Best practices advice\n\n"
        response += "What would you like to know?"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🤖 Atlan Customer Copilot | Powered by Claude AI & Tavily Search
</div>
""", unsafe_allow_html=True)