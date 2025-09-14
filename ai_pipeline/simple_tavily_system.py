#!/usr/bin/env python3
"""
Simple Tavily-Only System
Uses only Tavily for real-time documentation search
"""

import asyncio
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import sys
sys.path.append('ai_pipeline')

from sentiment_agent import SentimentAgent
from tavily_rag_integration import TavilyRAGIntegration

load_dotenv()

@dataclass
class TicketAnalysis:
    """Internal analysis of a ticket"""
    topic_tags: List[str]
    sentiment: str
    priority: str
    confidence: float
    reasoning: str

@dataclass
class TavilyResponse:
    """Response from Tavily system"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    is_tavily_used: bool
    routing_message: Optional[str] = None

class SimpleTavilySystem:
    """Simplified system using only Tavily for documentation search"""
    
    def __init__(self):
        self.sentiment_agent = None
        self.tavily_rag = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the system components"""
        try:
            print("🚀 Initializing Simple Tavily System...")
            
            # Clear any proxy environment variables that might cause issues
            proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'NO_PROXY', 'no_proxy']
            for var in proxy_vars:
                if var in os.environ:
                    print(f"🔧 Clearing proxy environment variable: {var}")
                    del os.environ[var]
            
            # Initialize sentiment agent for classification
            try:
                # Check if API key is available before initializing
                claude_key = os.getenv("CLAUDE_API_KEY")
                if claude_key:
                    self.sentiment_agent = SentimentAgent()
                    print("✅ Sentiment Agent initialized")
                else:
                    print("⚠️ CLAUDE_API_KEY not found - skipping Sentiment Agent")
                    self.sentiment_agent = None
            except Exception as e:
                print(f"⚠️ Sentiment Agent initialization failed: {e}")
                self.sentiment_agent = None
            
            # Initialize Tavily for real-time search
            try:
                # Check if API key is available before initializing
                tavily_key = os.getenv("TAVILY_API_KEY")
                if tavily_key:
                    self.tavily_rag = TavilyRAGIntegration()
                    print("✅ Tavily RAG Integration initialized")
                else:
                    print("⚠️ TAVILY_API_KEY not found - skipping Tavily RAG")
                    self.tavily_rag = None
            except Exception as e:
                print(f"⚠️ Tavily RAG Integration initialization failed: {e}")
                self.tavily_rag = None
            
            # Mark as initialized even if some components failed
            self.initialized = True
            print("✅ Simple Tavily System initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Simple Tavily System: {e}")
            # Don't raise the exception - allow the app to start with limited functionality
            self.initialized = False
    
    async def analyze_ticket(self, ticket_text: str) -> TicketAnalysis:
        """Analyze ticket using sentiment agent (internal analysis)"""
        if not self.sentiment_agent:
            raise Exception("Sentiment agent not initialized")
        
        classification = self.sentiment_agent.classify_ticket("", ticket_text)
        
        return TicketAnalysis(
            topic_tags=[tag.value for tag in classification.topic_tags],
            sentiment=classification.sentiment.value,
            priority=classification.priority.value,
            confidence=classification.confidence,
            reasoning=classification.reasoning
        )
    
    async def process_ticket(self, ticket_text: str) -> TavilyResponse:
        """Process ticket with Tavily-only pipeline"""
        if not self.initialized:
            await self.initialize()
        
        # Step 1: Internal Analysis (using sentiment agent)
        analysis = await self.analyze_ticket(ticket_text)
        
        # Step 2: Determine if we should use Tavily or route to team
        # STRICT RULE: Only use Tavily for specific topics
        tavily_topics = {"How-to", "Product", "Best practices", "API/SDK", "SSO"}
        should_use_tavily = any(tag in tavily_topics for tag in analysis.topic_tags)
        
        if should_use_tavily:
            # Use Tavily for real-time documentation search
            print(f"🔍 Using Tavily for topics: {[tag for tag in analysis.topic_tags if tag in tavily_topics]}")
            
            # Determine site type based on topics
            site_type = "both"  # Default to both
            if "API/SDK" in analysis.topic_tags:
                site_type = "devhub"  # Focus on developer.atlan.com
            elif any(tag in analysis.topic_tags for tag in ["Product", "Best practices", "SSO", "How-to"]):
                site_type = "docs"  # Focus on docs.atlan.com
            
            async with self.tavily_rag as tavily:
                # Search for real-time results with topic optimization
                search_results = await tavily.search_documentation(ticket_text, site_type, max_results=5, topic_tags=analysis.topic_tags)
                
                if not search_results:
                    return TavilyResponse(
                        answer="I couldn't find current information about this topic in the documentation.",
                        sources=[],
                        confidence=0.0,
                        is_tavily_used=True,
                        routing_message=None
                    )
                
                # Generate answer from real-time results
                realtime_response = await tavily.generate_realtime_answer(ticket_text, search_results, analysis.topic_tags)
                
                return TavilyResponse(
                    answer=realtime_response.answer,
                    sources=realtime_response.sources,
                    confidence=realtime_response.confidence,
                    is_tavily_used=True,
                    routing_message=None
                )
        else:
            # Route to appropriate team - STRICT RULE: No Tavily for these topics
            primary_topic = analysis.topic_tags[0] if analysis.topic_tags else "Other"
            
            # Create specific routing messages based on topic type
            routing_messages = {
                "Connector": "This ticket has been classified as a 'Connector' issue and routed to the appropriate team.",
                "Lineage": "This ticket has been classified as a 'Lineage' issue and routed to the appropriate team.",
                "Glossary": "This ticket has been classified as a 'Glossary' issue and routed to the appropriate team.",
                "Sensitive data": "This ticket has been classified as a 'Sensitive data' issue and routed to the appropriate team.",
                "Other": "This ticket has been classified as 'Other' and routed to the appropriate team."
            }
            
            routing_message = routing_messages.get(primary_topic, f"This ticket has been classified as a '{primary_topic}' issue and routed to the appropriate team.")
            
            print(f"🚫 Routing to team for topic: {primary_topic} (Tavily not used per strict rule)")
            
            return TavilyResponse(
                answer=routing_message,
                sources=[],
                confidence=1.0,
                is_tavily_used=False,
                routing_message=routing_message
            )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "system_type": "Simple Tavily System",
            "tavily_enabled": True,
            "sentiment_agent_ready": self.sentiment_agent is not None,
            "tavily_ready": self.tavily_rag is not None,
            "initialized": self.initialized
        }

# Global instance
simple_tavily_system = None

async def get_simple_tavily_system():
    """Get or create the global simple tavily system instance"""
    global simple_tavily_system
    if simple_tavily_system is None:
        simple_tavily_system = SimpleTavilySystem()
        await simple_tavily_system.initialize()
    return simple_tavily_system
