#!/usr/bin/env python3
"""
Atlan Customer Copilot - Streamlit Application
Interactive AI Agent with Real-time Documentation Search
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

# Import our AI pipeline components
from simple_tavily_system import get_simple_tavily_system
from file_parser import file_parser

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
    .response-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'simple_tavily_system' not in st.session_state:
    st.session_state.simple_tavily_system = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

@st.cache_resource
async def initialize_system():
    """Initialize the AI system with caching"""
    try:
        system = await get_simple_tavily_system()
        return system
    except Exception as e:
        st.error(f"Failed to initialize AI system: {str(e)}")
        return None

def display_analysis(analysis):
    """Display the internal analysis in a formatted way"""
    with st.expander("🔍 Internal Analysis", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sentiment", analysis.sentiment, delta=None)
            st.write("**Topic Tags:**")
            for tag in analysis.topic_tags:
                st.write(f"• {tag}")
        
        with col2:
            st.metric("Priority", analysis.priority, delta=None)
            confidence_percentage = round(analysis.confidence * 100)
            st.metric("Confidence", f"{confidence_percentage}%")
        
        with col3:
            st.write("**Reasoning:**")
            st.write(analysis.reasoning)

def display_response(response):
    """Display the final response"""
    if response.is_tavily_used:
        st.success("🎯 **AI Response Generated**")
        st.markdown("---")
        st.markdown(response.answer)
        
        if response.sources:
            st.markdown("---")
            st.write("**📚 Sources:**")
            for i, source in enumerate(response.sources, 1):
                with st.expander(f"Source {i}: {source['title'][:50]}..."):
                    st.write(f"**URL:** {source['url']}")
                    st.write(f"**Snippet:** {source['snippet']}")
    else:
        st.info("📋 **Routed to Team**")
        st.markdown("---")
        st.write(response.routing_message)

async def process_query(query: str):
    """Process a user query through the AI system"""
    if not st.session_state.simple_tavily_system:
        st.error("AI system not initialized. Please refresh the page.")
        return None
    
    try:
        # Show processing steps
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Analysis
        status_text.text("🧠 Analyzing query...")
        progress_bar.progress(25)
        
        analysis = await st.session_state.simple_tavily_system.analyze_ticket(query)
        
        # Step 2: Processing
        status_text.text("🔍 Processing with AI system...")
        progress_bar.progress(50)
        
        response = await st.session_state.simple_tavily_system.process_ticket(query)
        
        # Step 3: Complete
        status_text.text("✅ Complete!")
        progress_bar.progress(100)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return {
            'analysis': analysis,
            'response': response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'query': query
        }
        
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None

def process_uploaded_files(uploaded_files):
    """Process uploaded files and extract tickets"""
    if not uploaded_files:
        return []
    
    all_tickets = []
    
    for uploaded_file in uploaded_files:
        try:
            # Read file content
            file_content = uploaded_file.read()
            
            # Parse the file
            parse_result = file_parser.parse_file(uploaded_file.name, file_content)
            
            if parse_result['success']:
                # Extract tickets from the parsed content
                tickets = file_parser.extract_tickets_from_content(parse_result['content'])
                
                for ticket in tickets:
                    ticket['source_file'] = uploaded_file.name
                
                all_tickets.extend(tickets)
                st.success(f"✅ Processed {uploaded_file.name}: Found {len(tickets)} tickets")
            else:
                st.error(f"❌ Failed to parse {uploaded_file.name}: {parse_result['error']}")
                
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
    
    return all_tickets

async def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Atlan Customer Copilot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive AI Agent with Real-time Documentation Search</p>', unsafe_allow_html=True)
    
    # Initialize the AI system
    if st.session_state.simple_tavily_system is None:
        with st.spinner("🚀 Initializing AI system..."):
            st.session_state.simple_tavily_system = await initialize_system()
    
    if st.session_state.simple_tavily_system is None:
        st.error("❌ Failed to initialize the AI system. Please check your environment variables.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # System stats
        st.subheader("📊 System Status")
        stats = await st.session_state.simple_tavily_system.get_system_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("System Type", "Tavily")
        with col2:
            st.metric("Status", "✅ Ready" if stats['initialized'] else "❌ Not Ready")
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Export chat history
        if st.session_state.chat_history:
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="📥 Download Chat History",
                data=chat_json,
                file_name=f"atlan_copilot_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Interactive Chat", "📁 File Upload", "📊 Analytics"])
    
    with tab1:
        st.header("💬 Interactive Chat")
        
        # Chat input
        user_input = st.text_area(
            "Ask a question about Atlan:",
            placeholder="Example: How do I set up SSO authentication in Atlan?",
            height=100,
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            send_button = st.button("🚀 Send Query", type="primary")
        
        # Process query
        if send_button and user_input.strip():
            result = await process_query(user_input.strip())
            
            if result:
                # Add to chat history
                st.session_state.chat_history.append(result)
                
                # Display results
                st.markdown("---")
                
                # Display analysis
                display_analysis(result['analysis'])
                
                # Display response
                display_response(result['response'])
                
                # Clear input
                st.rerun()
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("📜 Chat History")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"Query {len(st.session_state.chat_history) - i}: {chat['query'][:50]}... ({chat['timestamp']})"):
                    st.write(f"**Original Query:** {chat['query']}")
                    display_analysis(chat['analysis'])
                    display_response(chat['response'])
    
    with tab2:
        st.header("📁 File Upload & Processing")
        
        st.write("Upload files to extract and analyze support tickets:")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'docx', 'csv', 'json', 'html', 'md', 'log', 'xml', 'yaml']
        )
        
        if uploaded_files:
            st.write(f"📁 {len(uploaded_files)} file(s) uploaded")
            
            if st.button("🔍 Process Files"):
                with st.spinner("Processing files..."):
                    tickets = process_uploaded_files(uploaded_files)
                    
                    if tickets:
                        st.success(f"✅ Successfully processed {len(tickets)} tickets")
                        
                        # Display tickets
                        for i, ticket in enumerate(tickets):
                            with st.expander(f"Ticket {i+1}: {ticket['subject'][:50]}..."):
                                st.write(f"**ID:** {ticket['id']}")
                                st.write(f"**Subject:** {ticket['subject']}")
                                st.write(f"**Source File:** {ticket.get('source_file', 'Unknown')}")
                                st.write(f"**Content:** {ticket['body'][:500]}...")
                                
                                # Process ticket with AI
                                if st.button(f"🤖 Analyze Ticket {i+1}", key=f"analyze_{i}"):
                                    result = await process_query(ticket['body'])
                                    if result:
                                        display_analysis(result['analysis'])
                                        display_response(result['response'])
                    else:
                        st.warning("⚠️ No tickets found in uploaded files")
    
    with tab3:
        st.header("📊 Analytics & Insights")
        
        if st.session_state.chat_history:
            # Calculate statistics
            total_queries = len(st.session_state.chat_history)
            
            # Sentiment distribution
            sentiment_counts = {}
            topic_counts = {}
            priority_counts = {}
            
            for chat in st.session_state.chat_history:
                analysis = chat['analysis']
                
                # Count sentiments
                sentiment = analysis.sentiment
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Count topics
                for topic in analysis.topic_tags:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                # Count priorities
                priority = analysis.priority
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Queries", total_queries)
            
            with col2:
                avg_confidence = sum(chat['analysis'].confidence for chat in st.session_state.chat_history) / total_queries
                st.metric("Avg Confidence", f"{round(avg_confidence * 100, 1)}%")
            
            with col3:
                tavily_used = sum(1 for chat in st.session_state.chat_history if chat['response'].is_tavily_used)
                st.metric("AI Responses", f"{tavily_used}/{total_queries}")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Sentiment Distribution")
                st.bar_chart(sentiment_counts)
            
            with col2:
                st.subheader("🏷️ Topic Distribution")
                st.bar_chart(topic_counts)
            
            # Priority distribution
            st.subheader("⚡ Priority Distribution")
            st.bar_chart(priority_counts)
            
            # Recent queries
            st.subheader("🕒 Recent Queries")
            for chat in st.session_state.chat_history[-5:]:
                with st.container():
                    st.write(f"**{chat['timestamp']}** - {chat['query'][:100]}...")
                    st.write(f"Sentiment: {chat['analysis'].sentiment} | Priority: {chat['analysis'].priority}")
                    st.markdown("---")
        else:
            st.info("No chat history available. Start a conversation to see analytics!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>🤖 Atlan Customer Copilot - Powered by Claude AI & Tavily Search</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    asyncio.run(main())
