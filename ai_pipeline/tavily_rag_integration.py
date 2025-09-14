#!/usr/bin/env python3
"""
Tavily Integration for Real-time RAG
Enhances the existing RAG system with real-time web crawling capabilities
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import aiohttp
from anthropic import Anthropic
from dotenv import load_dotenv
import hashlib
import time

load_dotenv()

@dataclass
class TavilySearchResult:
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None
    raw_content: Optional[str] = None

@dataclass
class EnhancedRAGResponse:
    answer: str
    sources: List[str]
    confidence: float
    evidence: Dict[str, Any]
    is_realtime: bool = False

class TavilyRAGIntegration:
    def __init__(self, tavily_api_key: str = None):
        """Initialize Tavily integration for real-time RAG"""
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        # Initialize Claude for answer generation
        claude_api_key = os.getenv("CLAUDE_API_KEY")
        if not claude_api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")
        
        self.llm_client = Anthropic(api_key=claude_api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        
        # Tavily API configuration
        self.tavily_base_url = "https://api.tavily.com"
        self.session = None
        
        # Documentation site configurations
        self.docs_sites = {
            "atlan_docs": {
                "base_url": "https://docs.atlan.com",
                "search_terms": ["atlan documentation", "atlan docs", "atlan product"],
                "include_domains": ["docs.atlan.com"],
                "exclude_domains": ["developer.atlan.com"],
                "description": "Atlan Product Documentation"
            },
            "atlan_devhub": {
                "base_url": "https://developer.atlan.com", 
                "search_terms": ["atlan api", "atlan developer", "atlan sdk", "atlan webhooks"],
                "include_domains": ["developer.atlan.com"],
                "exclude_domains": ["docs.atlan.com"],
                "description": "Atlan Developer Hub/API Documentation"
            }
        }
        
        print("✅ Tavily RAG Integration initialized")

    async def __aenter__(self):
        # Create connector without proxy settings
        connector = aiohttp.TCPConnector()
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'Authorization': f'Bearer {self.tavily_api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def search_documentation(self, query: str, site_type: str = "both", max_results: int = 5, topic_tags: List[str] = None) -> List[TavilySearchResult]:
        """Search documentation using Tavily API with optimized prompt-based guidance"""
        try:
            # Use optimized search prompt if topic_tags are provided
            if topic_tags:
                enhanced_query, optimized_site_type = self.get_optimized_search_prompt(query, topic_tags)
                site_type = optimized_site_type  # Override with optimized site type
                print(f"🔍 Using optimized search: '{enhanced_query}' on {site_type}")
            else:
                enhanced_query = query
                print(f"🔍 Using basic search: '{enhanced_query}' on {site_type}")
            
            # Determine which sites to search
            if site_type == "docs":
                sites = [self.docs_sites["atlan_docs"]]
            elif site_type == "devhub":
                sites = [self.docs_sites["atlan_devhub"]]
            else:
                sites = list(self.docs_sites.values())
            
            all_results = []
            
            for site_config in sites:
                # Use the enhanced query from optimization
                final_query = enhanced_query if topic_tags else query
                
                # Add site-specific targeting
                if not final_query.endswith(f"site:{site_config['base_url']}"):
                    final_query = f"{final_query} site:{site_config['base_url']}"
                
                # Tavily search parameters
                search_params = {
                    "query": final_query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_raw_content": True,
                    "max_results": max_results,
                    "include_domains": site_config.get("include_domains", []),
                    "exclude_domains": site_config.get("exclude_domains", []),
                    "include_images": False,
                    "include_raw_html": False
                }
                
                print(f"🔍 Searching {site_config['description']} for: {query}")
                
                # Make API request
                async with self.session.post(
                    f"{self.tavily_base_url}/search",
                    json=search_params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = self._process_tavily_results(data, site_config)
                        all_results.extend(results)
                        print(f"✅ Found {len(results)} results from {site_config['description']}")
                    else:
                        print(f"⚠️ Tavily API error for {site_config['description']}: {response.status}")
                        continue
                
                # Small delay between requests
                await asyncio.sleep(0.5)
            
            return all_results[:max_results]
            
        except Exception as e:
            print(f"❌ Error searching with Tavily: {e}")
            return []

    def _process_tavily_results(self, data: Dict, site_config: Dict) -> List[TavilySearchResult]:
        """Process Tavily API response into structured results"""
        results = []
        
        if "results" in data:
            for item in data["results"]:
                result = TavilySearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                    published_date=item.get("published_date"),
                    raw_content=item.get("raw_content")
                )
                results.append(result)
        
        return results

    def get_optimized_search_prompt(self, query: str, topic_tags: List[str]) -> Tuple[str, str]:
        """Generate optimized search prompt and determine site type based on query and topics"""
        
        # Determine primary topic for site selection
        primary_topic = topic_tags[0] if topic_tags else "Product"
        
        # Site selection based on topic
        if "API/SDK" in topic_tags:
            site_type = "devhub"
            site_guidance = "Search the Atlan Developer Hub (developer.atlan.com) for API documentation, SDK references, and developer resources."
        else:
            site_type = "docs" 
            site_guidance = "Search Atlan's main documentation (docs.atlan.com) for product features, user guides, and best practices."
        
        # Generate enhanced query with prompt-based guidance
        base_query = query.lower()
        
        # Add topic-specific guidance terms
        if "API/SDK" in topic_tags:
            enhanced_query = f"{query} API documentation SDK developer guide"
            search_context = "Focus on API endpoints, SDK methods, authentication, and integration examples."
        elif "Product" in topic_tags:
            enhanced_query = f"{query} product features user guide documentation"
            search_context = "Focus on product capabilities, user workflows, and feature documentation."
        elif "How-to" in topic_tags:
            enhanced_query = f"{query} how to tutorial step by step guide"
            search_context = "Focus on step-by-step instructions, tutorials, and implementation guides."
        elif "SSO" in topic_tags:
            enhanced_query = f"{query} single sign on authentication setup configuration"
            search_context = "Focus on SSO setup, authentication configuration, and security settings."
        elif "Best practices" in topic_tags:
            enhanced_query = f"{query} best practices recommendations guidelines"
            search_context = "Focus on recommended approaches, optimization strategies, and best practices."
        else:
            enhanced_query = query
            search_context = "General documentation search."
        
        # Create comprehensive search prompt
        search_prompt = f"""
        {site_guidance}
        
        Search Context: {search_context}
        
        Query: {enhanced_query}
        
        Instructions:
        - Prioritize official documentation pages
        - Include relevant code examples and configurations
        - Focus on current and up-to-date information
        - Ensure results are directly actionable
        """
        
        print(f"🎯 Search optimization - Topic: {primary_topic}, Site: {site_type}")
        print(f"📝 Search context: {search_context}")
        
        return enhanced_query, site_type

    async def generate_realtime_answer(self, query: str, search_results: List[TavilySearchResult], 
                                     topic_tags: List[str] = None) -> EnhancedRAGResponse:
        """Generate answer using real-time search results"""
        try:
            if not search_results:
                return EnhancedRAGResponse(
                    answer="I couldn't find current information about this topic in the documentation.",
                    sources=[],
                    confidence=0.0,
                    evidence={"search_results": 0},
                    is_realtime=True
                )
            
            # Prepare context from search results for better summarization
            context_parts = []
            sources = []
            
            for i, result in enumerate(search_results):
                # Include more structured information for better summarization
                context_parts.append(f"""**Source {i+1}: {result.title}**
URL: {result.url}
Relevance Score: {result.score:.2f}
Content: {result.content}

---""")
                # Create structured source objects instead of just URLs
                source_obj = {
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.content[:200] + "..." if len(result.content) > 200 else result.content
                }
                # Avoid duplicates
                if not any(s["url"] == result.url for s in sources):
                    sources.append(source_obj)
            
            context = "\n\n".join(context_parts)
            
            # Calculate confidence based on search scores
            avg_score = sum(result.score for result in search_results) / len(search_results)
            confidence = min(1.0, avg_score)
            
            # Generate answer using Claude with enhanced summarization
            prompt = f"""You are an expert Atlan support assistant. Summarize and synthesize the current documentation to provide a comprehensive answer to the user's question.

Question: {query}

Current Documentation Context:
{context}

Instructions:
1. **Summarize** the key information from the documentation sources
2. **Synthesize** multiple sources into a coherent, comprehensive answer
3. **Structure** your response with clear sections (Overview, Steps, Key Points, etc.)
4. **Prioritize** the most relevant and recent information
5. **Extract** specific steps, features, or configurations mentioned
6. **CRITICAL: DO NOT include any source URLs, links, or "Sources:" sections in your response** - sources will be provided separately
7. **Highlight** any important prerequisites, requirements, or limitations
8. **Provide** actionable guidance based on the documentation

Response Format:
- Start with a brief overview
- Include specific steps or details with code examples if relevant
- Mention any important considerations
- Use clear, professional language
- Focus purely on the content, never mention sources or links
- Keep the response concise but comprehensive
- End with practical next steps if applicable

Answer:"""

            response = self.llm_client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.1,
                system="You are an expert Atlan support assistant specializing in summarizing and synthesizing documentation. Your role is to:\n\n1. **Summarize** complex documentation into clear, actionable guidance\n2. **Synthesize** information from multiple sources into coherent responses\n3. **Structure** answers with clear sections and bullet points\n4. **Extract** key steps, requirements, and important details\n5. **Provide** comprehensive yet concise answers\n6. **Reference** sources naturally within your responses\n\nAlways prioritize accuracy, clarity, and actionable guidance based on the current Atlan documentation.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = response.content[0].text.strip()
            
            # Clean up any source URLs that might have been included in the answer
            # Remove common source patterns
            import re
            
            # Remove various source patterns (more aggressive cleaning)
            answer = re.sub(r'\*\*Sources?:\*\*\s*\n.*', '', answer, flags=re.MULTILINE | re.DOTALL)
            answer = re.sub(r'\n\s*•\s*https?://[^\s]+', '', answer)
            answer = re.sub(r'\n\s*🔗\s*https?://[^\s]+', '', answer)
            answer = re.sub(r'\n\s*\*\*📚\s*Sources?:\*\*\s*\n.*', '', answer, flags=re.MULTILINE | re.DOTALL)
            answer = re.sub(r'\*\*📚\s*Sources?:\*\*.*', '', answer, flags=re.MULTILINE | re.DOTALL)
            
            # Remove any remaining URL patterns
            answer = re.sub(r'\n\s*https?://[^\s]+', '', answer)
            answer = re.sub(r'https?://[^\s]+', '', answer)  # Remove any standalone URLs
            
            # Remove any lines that start with source-related keywords
            answer = re.sub(r'\n\s*(Sources?|Links?|References?):\s*\n.*', '', answer, flags=re.MULTILINE | re.DOTALL)
            
            # Remove any developer.atlan.com or docs.atlan.com URLs specifically
            answer = re.sub(r'https?://(developer|docs)\.atlan\.com[^\s]*', '', answer)
            
            # Remove any trailing empty lines and clean up
            answer = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer)
            answer = answer.strip()
            
            return EnhancedRAGResponse(
                answer=answer,
                sources=sources,
                confidence=confidence,
                evidence={
                    "search_results": len(search_results),
                    "avg_score": avg_score,
                    "search_type": "realtime"
                },
                is_realtime=True
            )
            
        except Exception as e:
            print(f"❌ Error generating realtime answer: {e}")
            return EnhancedRAGResponse(
                answer=f"Error generating answer: {str(e)}",
                sources=[],
                confidence=0.0,
                evidence={"error": str(e)},
                is_realtime=True
            )

    async def should_use_realtime_search(self, query: str, topic_tags: List[str], 
                                       static_confidence: float) -> bool:
        """Determine if real-time search should be used - STRICT RULE"""
        # STRICT RULE: Only use Tavily for specific topics
        tavily_allowed_topics = {"How-to", "Product", "Best practices", "API/SDK", "SSO"}
        
        # Check if any topic tag is in the allowed list
        has_allowed_topics = any(tag in tavily_allowed_topics for tag in topic_tags)
        
        if not has_allowed_topics:
            print(f"🚫 Tavily not used - topic tags {topic_tags} not in allowed list {tavily_allowed_topics}")
            return False
        
        # For allowed topics, use additional criteria for optimization
        time_sensitive_keywords = [
            "latest", "new", "recent", "updated", "current", "2024", "2025",
            "recently", "just released", "new feature", "latest version"
        ]
        
        # Check for time-sensitive keywords
        query_lower = query.lower()
        has_time_keywords = any(keyword in query_lower for keyword in time_sensitive_keywords)
        
        # Use real-time if static confidence is low OR has time-sensitive indicators OR is allowed topic
        return static_confidence < 0.7 or has_time_keywords or has_allowed_topics

    async def hybrid_search(self, query: str, topic_tags: List[str], 
                           static_answer: str, static_confidence: float) -> EnhancedRAGResponse:
        """Perform hybrid search combining static and real-time results"""
        try:
            # Determine if we should use real-time search
            use_realtime = await self.should_use_realtime_search(query, topic_tags, static_confidence)
            
            if not use_realtime:
                return EnhancedRAGResponse(
                    answer=static_answer,
                    sources=[],
                    confidence=static_confidence,
                    evidence={"search_type": "static_only"},
                    is_realtime=False
                )
            
            # Perform real-time search
            search_results = await self.search_documentation(query, "both", max_results=5)
            
            if not search_results:
                # Fallback to static answer if no real-time results
                return EnhancedRAGResponse(
                    answer=static_answer,
                    sources=[],
                    confidence=static_confidence,
                    evidence={"search_type": "static_fallback"},
                    is_realtime=False
                )
            
            # Generate answer from real-time results
            return await self.generate_realtime_answer(query, search_results, topic_tags)
            
        except Exception as e:
            print(f"❌ Error in hybrid search: {e}")
            return EnhancedRAGResponse(
                answer=static_answer,
                sources=[],
                confidence=static_confidence,
                evidence={"error": str(e)},
                is_realtime=False
            )

# Example usage and testing
async def test_tavily_integration():
    """Test the Tavily integration"""
    async with TavilyRAGIntegration() as tavily_rag:
        # Test query
        query = "How do I set up SSO authentication in Atlan?"
        topic_tags = ["SSO", "Authentication"]
        
        # Simulate static RAG response
        static_answer = "SSO setup involves configuring your identity provider..."
        static_confidence = 0.6
        
        # Perform hybrid search
        result = await tavily_rag.hybrid_search(query, topic_tags, static_answer, static_confidence)
        
        print(f"Query: {query}")
        print(f"Answer: {result.answer}")
        print(f"Sources: {result.sources}")
        print(f"Confidence: {result.confidence}")
        print(f"Real-time: {result.is_realtime}")

if __name__ == "__main__":
    asyncio.run(test_tavily_integration())
