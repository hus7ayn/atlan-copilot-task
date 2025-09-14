#!/usr/bin/env python3
"""
Tavily Configuration for Atlan Customer Copilot
Configuration settings for Tavily API integration
"""

# Tavily API Configuration
TAVILY_CONFIG = {
    "api_key": None,  # Set via environment variable TAVILY_API_KEY
    "base_url": "https://api.tavily.com",
    "timeout": 30,
    "max_retries": 3,
    "rate_limit_delay": 0.5,  # Delay between requests in seconds
}

# Documentation Site Configurations
DOCS_SITES = {
    "atlan_docs": {
        "base_url": "https://docs.atlan.com",
        "search_terms": [
            "atlan documentation",
            "atlan docs", 
            "atlan user guide",
            "atlan getting started"
        ],
        "include_domains": ["docs.atlan.com"],
        "exclude_domains": ["developer.atlan.com", "blog.atlan.com"],
        "search_depth": "advanced",
        "max_results": 5
    },
    "atlan_devhub": {
        "base_url": "https://developer.atlan.com",
        "search_terms": [
            "atlan api",
            "atlan developer",
            "atlan sdk",
            "atlan webhooks"
        ],
        "include_domains": ["developer.atlan.com"],
        "exclude_domains": ["docs.atlan.com", "blog.atlan.com"],
        "search_depth": "advanced", 
        "max_results": 5
    }
}

# Search Parameters for Different Query Types
SEARCH_PARAMETERS = {
    "general": {
        "search_depth": "basic",
        "include_answer": True,
        "include_raw_content": False,
        "include_images": False,
        "include_raw_html": False,
        "max_results": 5
    },
    "detailed": {
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True,
        "include_images": False,
        "include_raw_html": False,
        "max_results": 8
    },
    "comprehensive": {
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": True,
        "include_images": False,
        "include_raw_html": True,
        "max_results": 10
    }
}

# Query Classification for Search Strategy
QUERY_CLASSIFICATION = {
    "realtime_keywords": [
        "latest", "new", "recent", "updated", "current", "2024", "2025",
        "recently", "just released", "new feature", "latest version",
        "what's new", "changelog", "release notes", "recent changes"
    ],
    "realtime_topics": [
        "API/SDK", "Product", "How-to", "SSO", "Connector", "Lineage"
    ],
    "static_topics": [
        "Glossary", "Sensitive data", "Other"
    ],
    "high_priority_queries": [
        "authentication", "sso", "security", "error", "troubleshoot",
        "setup", "configuration", "installation"
    ]
}

# Confidence Thresholds
CONFIDENCE_THRESHOLDS = {
    "static_rag_min": 0.7,  # Minimum confidence to use static RAG only
    "realtime_trigger": 0.6,  # Confidence below which to trigger real-time search
    "hybrid_threshold": 0.5,  # Minimum confidence for hybrid approach
    "fallback_threshold": 0.3  # Below this, use fallback responses
}

# Rate Limiting and Performance
PERFORMANCE_CONFIG = {
    "max_concurrent_searches": 3,
    "search_timeout": 30,
    "cache_duration": 300,  # 5 minutes
    "retry_delay": 1.0,
    "max_retries": 2
}

# Content Filtering
CONTENT_FILTERS = {
    "min_content_length": 100,
    "max_content_length": 5000,
    "exclude_patterns": [
        r".*\.pdf$",
        r".*\.jpg$", 
        r".*\.png$",
        r".*\.gif$",
        r".*\.css$",
        r".*\.js$",
        r".*\.xml$"
    ],
    "include_patterns": [
        r".*docs\.atlan\.com.*",
        r".*developer\.atlan\.com.*"
    ]
}

# Response Templates
RESPONSE_TEMPLATES = {
    "no_results": "I couldn't find current information about this topic in the documentation.",
    "error_fallback": "I encountered an error while searching for information. Please try rephrasing your question.",
    "realtime_prefix": "Based on the latest documentation, ",
    "static_prefix": "Based on the documentation, ",
    "hybrid_prefix": "Based on both the documentation and latest information, "
}

# Monitoring and Logging
LOGGING_CONFIG = {
    "log_searches": True,
    "log_performance": True,
    "log_errors": True,
    "log_level": "INFO"
}
