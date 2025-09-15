"""
Atlan Customer Copilot AI Pipeline

This package contains the AI components for classifying customer support tickets,
including sentiment analysis, topic classification, and priority assignment.
"""

from .sentiment_agent import SentimentAgent, ClassificationResult, TopicTag, Sentiment, Priority

__all__ = [
    'SentimentAgent',
    'ClassificationResult',
    'TopicTag',
    'Sentiment',
    'Priority'
]
