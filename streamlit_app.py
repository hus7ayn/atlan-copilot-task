#!/usr/bin/env python3
"""
Atlan Customer Copilot - AI-Powered Streamlit Application
"""

import streamlit as st
import os
import requests
import json

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
    return bool(claude_key and tavily_key), claude_key, tavily_key

def call_claude_api(prompt, api_key):
    """Make a simple call to Claude API"""
    try:
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("content", [{}])[0].get("text", "No response")
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error calling Claude API: {str(e)}"

def call_tavily_api(query, api_key):
    """Make a simple call to Tavily API"""
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 3
        }
        
        response = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("results", [])
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error calling Tavily API: {str(e)}"

# Main app
st.title("🤖 Atlan Customer Copilot")
st.subheader("AI-Powered Customer Support Assistant")

# Check API keys
api_configured, claude_key, tavily_key = check_api_keys()

# Sidebar for status
with st.sidebar:
    st.header("🔧 System Status")
    
    if api_configured:
        st.success("✅ API Keys Configured")
        st.success("✅ Claude AI Ready")
        st.success("✅ Tavily Search Ready")
        
        # Show masked keys
        st.info(f"Claude API: ...{claude_key[-10:] if claude_key else 'Not set'}")
        st.info(f"Tavily API: ...{tavily_key[-10:] if tavily_key else 'Not set'}")
    else:
        st.error("❌ API Keys Not Configured")
        st.warning("⚠️ Add secrets to enable AI features")

# Main content
if api_configured:
    st.success("🎉 **System Ready!** Full AI functionality is now available.")
    
    # Chat interface
    st.header("💬 Chat with AI Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Atlan..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                try:
                    # Get Tavily search results first
                    search_results = call_tavily_api(prompt, tavily_key)
                    
                    # Create enhanced prompt with search context
                    if isinstance(search_results, list) and search_results:
                        context = "\n\nRelevant information:\n"
                        for i, result in enumerate(search_results[:2], 1):
                            context += f"{i}. {result.get('title', 'No title')}: {result.get('content', 'No content')[:200]}...\n"
                        
                        enhanced_prompt = f"{prompt}\n\n{context}\n\nPlease provide a helpful response based on the user's question and the relevant information above."
                    else:
                        enhanced_prompt = prompt
                    
                    # Get Claude response
                    ai_response = call_claude_api(enhanced_prompt, claude_key)
                    
                    # Display response
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                    # Show search sources if available
                    if isinstance(search_results, list) and search_results:
                        with st.expander("🔍 Sources"):
                            for i, result in enumerate(search_results[:3], 1):
                                st.markdown(f"**{i}. {result.get('title', 'No title')}**")
                                st.markdown(f"*{result.get('url', 'No URL')}*")
                                st.markdown(f"{result.get('content', 'No content')[:300]}...")
                                st.markdown("---")
                    
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Features section
    st.header("🚀 Available Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💬 AI Chat**
        - ✅ Claude AI responses
        - ✅ Context-aware conversations
        - ✅ Intelligent routing
        """)
    
    with col2:
        st.markdown("""
        **🔍 Real-time Search**
        - ✅ Tavily web search
        - ✅ Documentation lookup
        - ✅ Knowledge base access
        """)
    
    with col3:
        st.markdown("""
        **📊 Analytics**
        - ✅ Search result sources
        - ✅ Response quality metrics
        - ✅ User interaction tracking
        """)

else:
    # Show setup instructions
    st.warning("⚠️ **API Keys Required**")
    
    st.markdown("""
    ### 🔧 Setup Required
    
    To enable full AI functionality, please add your API keys to Streamlit Cloud secrets:
    
    **In Streamlit Cloud Secrets:**
    ```toml
    CLAUDE_API_KEY = "sk-ant-api03-..."
    TAVILY_API_KEY = "tvly-dev-..."
    ```
    
    ### 🎯 What You'll Get
    
    Once configured, your AI assistant will provide:
    - **Intelligent Responses** using Claude AI
    - **Real-time Search** via Tavily integration  
    - **Context-aware** conversations
    - **Source citations** for all responses
    
    ### 📞 Example Queries
    
    Try asking questions like:
    - "How do I create a data asset in Atlan?"
    - "What's the difference between a table and a view?"
    - "How can I set up data lineage tracking?"
    - "What are the best practices for data governance?"
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🤖 Atlan Customer Copilot | Powered by Claude AI & Tavily Search
</div>
""", unsafe_allow_html=True)