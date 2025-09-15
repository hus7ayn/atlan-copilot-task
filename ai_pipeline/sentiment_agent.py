"""
AI-powered ticket classification system for customer support.
Classifies tickets by topic, sentiment, and priority using Claude AI models.
"""

import json
import re
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

class TopicTag(Enum):
    HOW_TO = "How-to"
    PRODUCT = "Product"
    CONNECTOR = "Connector"
    LINEAGE = "Lineage"
    API_SDK = "API/SDK"
    SSO = "SSO"
    GLOSSARY = "Glossary"
    BEST_PRACTICES = "Best practices"
    SENSITIVE_DATA = "Sensitive data"
    OTHER = "Other"

class Sentiment(Enum):
    FRUSTRATED = "Frustrated"
    CURIOUS = "Curious"
    ANGRY = "Angry"
    NEUTRAL = "Neutral"
    CONFUSED = "Confused"

class Priority(Enum):
    P0 = "P0 (High)"
    P1 = "P1 (Medium)"
    P2 = "P2 (Low)"

@dataclass
class ClassificationResult:
    topic_tags: List[TopicTag]
    sentiment: Sentiment
    priority: Priority
    confidence: float
    reasoning: str

class SentimentAgent:
    def __init__(self):
        # Use the provided Grok API key from environment
        self.api_key = os.getenv("GROK_API_KEY")
        print(f"🔍 SentimentAgent - GROK_API_KEY present: {bool(self.api_key)}")
        if self.api_key:
            print(f"🔍 SentimentAgent - GROK_API_KEY starts with: {self.api_key[:10]}...")
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is required")
        
        print(f"🔍 SentimentAgent - Initializing Grok client with key: {self.api_key[:10]}...")
        print(f"🔍 SentimentAgent - Full API key length: {len(self.api_key)}")
        print(f"🔍 SentimentAgent - API key starts with: {self.api_key[:20]}...")
        
        # Initialize Grok client with Railway-compatible settings
        try:
            self.client = Groq(
                api_key=self.api_key,
                timeout=30.0,
                max_retries=3
            )
            print("✅ Grok client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Grok client: {e}")
            # Try with explicit HTTP client configuration
            import httpx
            self.client = Groq(
                api_key=self.api_key,
                http_client=httpx.Client(timeout=30.0, limits=httpx.Limits(max_connections=10))
            )
            print("✅ Grok client initialized with httpx fallback")
        
        self.model = os.getenv("GROK_MODEL", "gemma2-9b-it")
        self.temperature = float(os.getenv("GROK_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("GROK_MAX_TOKENS", "1000"))
        
        print("✅ Grok API client initialized successfully")
        
        # Add caching for API responses to reduce API calls
        self._cache = {}
        self._cache_max_size = 1000
        
        # New Prioritization System - 6 Factors with Specific Scoring Formula
        # Final Priority Score = Urgency×1.5 + BusinessImpact×1.2 + Severity×1.3 + Compliance×1.4 + Deadline×1.3 + Sentiment×1.1
        
        # 1. URGENCY INDICATORS (0-3 scale)
        self.urgency_indicators = {
            # Score 3 (very urgent)
            'urgent': 3, 'critical failure': 3, 'emergency': 3, 'asap': 3, 'immediately': 3,
            'blocked': 3, 'deadline approaching': 3, 'down': 3, 'broken': 3, 'failed': 3,
            'not working': 3, 'crash': 3, 'unavailable': 3,
            
            # Score 2 (urgent)
            'important': 2, 'priority': 2, 'soon': 2, 'quickly': 2, 'fast': 2,
            'issue': 2, 'problem': 2, 'error': 2, 'bug': 2,
            
            # Score 1 (somewhat urgent)
            'help': 1, 'assistance': 1, 'support': 1, 'question': 1,
            
            # Score 0 (not urgent)
            'wondering': 0, 'curious': 0, 'learning': 0, 'explore': 0, 'understand': 0
        }
        
        # 2. BUSINESS IMPACT INDICATORS (0-3 scale)
        self.business_impact_indicators = {
            # Score 3 (organization-wide)
            'entire organization': 3, 'all users': 3, 'everyone': 3, 'company-wide': 3,
            'organization': 3, 'enterprise': 3, 'all teams': 3, 'global': 3,
            
            # Score 2 (team/department)
            'team': 2, 'department': 2, 'bi team': 2, 'engineering': 2, 'data team': 2,
            'analytics team': 2, 'multiple users': 2, 'several people': 2,
            
            # Score 1 (small group)
            'few users': 1, 'small group': 1, 'couple of people': 1, 'some users': 1,
            
            # Score 0 (individual)
            'individual': 0, 'personal': 0, 'just me': 0, 'myself': 0, 'single user': 0
        }
        
        # 3. SEVERITY INDICATORS (0-3 scale)
        self.severity_indicators = {
            # Score 3 (break/failure in production)
            'production': 3, 'live': 3, 'down': 3, 'broken': 3, 'failed': 3, 'crash': 3,
            'not working': 3, 'unavailable': 3, 'outage': 3, 'disruption': 3,
            
            # Score 2 (security/compliance concern OR setup/config problem)
            'security': 2, 'compliance': 2, 'audit': 2, 'pii': 2, 'sensitive': 2,
            'rbac': 2, 'dlp': 2, 'sso': 2, 'authentication': 2, 'credentials': 2,
            'setup': 2, 'configuration': 2, 'config': 2, 'install': 2, 'deploy': 2,
            'integration': 2, 'connector': 2, 'api': 2, 'permissions': 2,
            
            # Score 1 (feature request or how-to)
            'how to': 1, 'how-to': 1, 'tutorial': 1, 'guide': 1, 'feature request': 1,
            'enhancement': 1, 'improvement': 1, 'suggestion': 1, 'question': 1,
            
            # Score 0 (general info/curiosity)
            'info': 0, 'information': 0, 'curious': 0, 'wondering': 0, 'learning': 0,
            'explore': 0, 'understand': 0, 'glossary': 0, 'definition': 0
        }
        
        # 4. COMPLIANCE & SECURITY RISK INDICATORS (0-3 scale)
        self.compliance_security_indicators = {
            # Score 3 (high risk)
            'audit': 3, 'compliance': 3, 'regulatory': 3, 'sox': 3, 'gdpr': 3, 'hipaa': 3,
            'pii': 3, 'sensitive data': 3, 'confidential': 3, 'breach': 3, 'leak': 3,
            'exposed': 3, 'security breach': 3, 'data loss': 3,
            
            # Score 2 (medium risk)
            'rbac': 2, 'dlp': 2, 'sso': 2, 'authentication': 2, 'credentials': 2,
            'permissions': 2, 'access control': 2, 'authorization': 2, 'privacy': 2,
            
            # Score 1 (low risk)
            'security': 1, 'best practices': 1, 'governance': 1, 'policy': 1,
            
            # Score 0 (no risk)
            'general': 0, 'info': 0, 'question': 0, 'how to': 0, 'tutorial': 0
        }
        
        # 5. DEADLINE SENSITIVITY INDICATORS (0-2 scale)
        self.deadline_indicators = {
            # Score 2 (deadline soon)
            'deadline': 2, 'due': 2, 'presentation': 2, 'meeting': 2, 'tomorrow': 2,
            'today': 2, 'this week': 2, 'next week': 2, 'urgent': 2, 'asap': 2,
            'immediately': 2, 'critical': 2, 'emergency': 2,
            
            # Score 1 (some deadline)
            'soon': 1, 'quickly': 1, 'priority': 1, 'important': 1, 'timely': 1,
            
            # Score 0 (no deadline)
            'whenever': 0, 'no rush': 0, 'curious': 0, 'learning': 0, 'explore': 0
        }
        
        # 6. SENTIMENT/FRUSTRATION INDICATORS (0-2 scale)
        self.sentiment_indicators = {
            # Score 2 (high frustration)
            'angry': 2, 'frustrated': 2, 'annoyed': 2, 'upset': 2, 'irritated': 2,
            'mad': 2, 'furious': 2, 'exasperated': 2, 'fed up': 2, 'disappointed': 2,
            
            # Score 1 (some frustration)
            'concerned': 1, 'worried': 1, 'confused': 1, 'stuck': 1, 'struggling': 1,
            'difficult': 1, 'challenging': 1, 'problem': 1, 'issue': 1,
            
            # Score 0 (neutral)
            'neutral': 0, 'curious': 0, 'wondering': 0, 'learning': 0, 'explore': 0,
            'question': 0, 'help': 0, 'assistance': 0, 'support': 0
        }
        
        # Priority thresholds based on final score (adjusted for more realistic distribution)
        self.priority_thresholds = {
            Priority.P0: 9,  # High (score ≥ 15) - Only truly critical issues
            Priority.P1: 6,   # Medium (score 8-14) - Important issues
            Priority.P2: 4    # Low (score ≤ 7) - Standard issues
        }
        
        # Define classification prompts optimized for Llama 3.1
        self.topic_prompt = """
        Classify this ticket into the most appropriate category. Consider the main focus and context of the user's request.

        Categories:
        - How-to: Questions about how to use features, step-by-step instructions, tutorials, or guidance on performing specific tasks
        - Product: General product questions, feature requests, bug reports, or issues related to core Atlan functionality
        - Connector: Questions about connecting external data sources, database integrations, or third-party tool connections
        - Lineage: Questions about data lineage, data flow, dependencies, or understanding how data moves through systems
        - API/SDK: Questions about programmatic access, API usage, SDK implementation, or developer integrations
        - SSO: Questions about single sign-on, authentication, user management, or security access controls
        - Glossary: Questions about business glossary, data definitions, terminology, or metadata management
        - Best practices: Questions about recommended approaches, governance, compliance, or optimization strategies
        - Sensitive data: Questions about data privacy, PII handling, security classifications, or compliance requirements
        - Other: Questions that don't fit into the above categories or are too general to classify

        Subject: {subject}
        Body: {body}

        {{"topics": ["category_name"]}}
        """

        self.sentiment_prompt = """
        Analyze the sentiment of this customer support ticket. Consider the tone, urgency, and emotional state of the user.

        Categories:
        - Neutral: The ticket is written in a professional, objective, or matter-of-fact tone. The user is calm and simply asking a question or making a routine request, without expressing strong emotions.
        - Curious: The user is seeking to learn, explore, or understand something new. The tone is inquisitive, open, and interested, often asking for information, guidance, or clarification out of curiosity rather than frustration.
        - Confused: The user expresses uncertainty, lack of understanding, or is lost about a process, feature, or outcome. The tone indicates the user needs clarification or help to resolve their confusion.
        - Frustrated: The user is annoyed, blocked, or experiencing repeated issues. The tone shows irritation or impatience, but does not rise to the level of anger or hostility.
        - Angry: The user is openly hostile, very upset, or uses strong negative language. The tone is aggressive, accusatory, or indicates significant dissatisfaction or outrage.
        Subject: {subject}
        Body: {body}

        Respond with JSON only:
        {{"sentiment": "category"}}
        """

    def analyze_sentiment(self, subject: str, body: str) -> List[Dict]:
        """
        Analyze ticket text and classify sentiment using the LLM
        Returns list of sentiment results compatible with existing system.
        """
        try:
            # Get sentiment classification from Llama 3.1
            sentiment_response = self._get_llm_response(
                self.sentiment_prompt.format(subject=subject, body=body)
            )
            sentiment_data = self._parse_json_response(sentiment_response)
            
            # Convert to expected format and validate
            sentiment_label = sentiment_data.get("sentiment", "Neutral")
            
            # Normalize case and validate that the sentiment is one of our allowed values
            valid_sentiments = ["Neutral", "Curious", "Confused", "Frustrated", "Angry"]
            sentiment_label = sentiment_label.capitalize()  # Normalize case
            
            if sentiment_label not in valid_sentiments:
                print(f"⚠️ Invalid sentiment '{sentiment_label}' returned, defaulting to 'Neutral'")
                sentiment_label = "Neutral"
            
            confidence = 0.9  # High confidence for LLM classification
            
            return [{"label": sentiment_label, "confidence": confidence}]
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return [{"label": "Neutral", "confidence": 0.5}]

    def _calculate_priority_score(self, topic_tags: List[TopicTag], sentiment: Sentiment, subject: str = "", body: str = "") -> Tuple[Priority, float, str]:
        """Calculate priority using the exact 6-factor formula specified."""
        
        text = (subject + " " + body).lower()
        
        # 1. URGENCY (0-3 scale)
        urgency_score = self._get_max_keyword_score(text, self.urgency_indicators, default=0)
        
        # 2. BUSINESS IMPACT (0-3 scale)
        business_impact_score = self._get_max_keyword_score(text, self.business_impact_indicators, default=0)
        
        # 3. SEVERITY (0-3 scale)
        severity_score = self._get_max_keyword_score(text, self.severity_indicators, default=0)
        
        # 4. COMPLIANCE & SECURITY RISK (0-3 scale)
        compliance_score = self._get_max_keyword_score(text, self.compliance_security_indicators, default=0)
        
        # 5. DEADLINE SENSITIVITY (0-2 scale)
        deadline_score = self._get_max_keyword_score(text, self.deadline_indicators, default=0)
        
        # 6. SENTIMENT/FRUSTRATION (0-2 scale)
        sentiment_score = self._get_max_keyword_score(text, self.sentiment_indicators, default=0)
        
        # Apply the exact formula: Urgency×1.5 + BusinessImpact×1.2 + Severity×1.3 + Compliance×1.4 + Deadline×1.3 + Sentiment×1.1
        final_score = (
            urgency_score * 1.7 +
            business_impact_score * 1.2 +
            severity_score * 1.3 +
            compliance_score * 1.4 +
            deadline_score * 1.3 +
            sentiment_score * 1.1
        )
        
        # Round to nearest integer
        final_score = round(final_score)
        
        # Determine priority based on thresholds
        if final_score >= self.priority_thresholds[Priority.P0]:
            priority = Priority.P0
        elif final_score >= self.priority_thresholds[Priority.P1]:
            priority = Priority.P1
        else:
            priority = Priority.P2
        
        # Generate simple reasoning for speed
        reasoning = f"Priority: {priority.value} (Score: {final_score})"
        
        return priority, final_score, reasoning
    
    def _get_max_keyword_score(self, text: str, keyword_dict: dict, default: float = 0.0) -> float:
        """Get the maximum score for any matching keywords in the text."""
        max_score = default
        
        for keyword, score in keyword_dict.items():
            if keyword in text:
                max_score = max(max_score, score)
        
        return max_score
    
    def _generate_new_priority_reasoning(self, final_score: int, urgency_score: int, business_impact_score: int, 
                                       severity_score: int, compliance_score: int, deadline_score: int, 
                                       sentiment_score: int, priority: Priority) -> str:
        """Generate detailed reasoning for the new 6-factor priority system."""
        
        reasoning_parts = [
            f"🎯 Final Score: {final_score} (rounded)",
            f"⚡ Urgency: {urgency_score}/3 (×1.5 = {urgency_score * 1.5})",
            f"🏢 Business Impact: {business_impact_score}/3 (×1.2 = {business_impact_score * 1.2})",
            f"🔧 Severity: {severity_score}/3 (×1.3 = {severity_score * 1.3})",
            f"🔒 Compliance/Security: {compliance_score}/3 (×1.4 = {compliance_score * 1.4})",
            f"⏰ Deadline: {deadline_score}/2 (×1.3 = {deadline_score * 1.3})",
            f"😊 Sentiment: {sentiment_score}/2 (×1.1 = {sentiment_score * 1.1})",
            f"📊 Priority: {priority.value} (threshold: {self.priority_thresholds[priority]})"
        ]
        
        return " | ".join(reasoning_parts)

    def classify_ticket(self, subject: str, body: str) -> ClassificationResult:
        """Classify a support ticket into topic, sentiment, and priority."""
        
        try:
            # Get topic classification
            topic_response = self._get_llm_response(
                self.topic_prompt.format(subject=subject, body=body)
            )
            topic_data = self._parse_json_response(topic_response)
            
            # Get sentiment classification
            sentiment_response = self._get_llm_response(
                self.sentiment_prompt.format(subject=subject, body=body)
            )
            sentiment_data = self._parse_json_response(sentiment_response)
        except Exception as e:
            raise RuntimeError(f"❌ API call failed: {e}")
        
        # Convert to enums with error handling
        try:
            # Handle both "topics" array and "category" string formats
            if "topics" in topic_data:
                topics = topic_data.get("topics", ["How-to"])
                if not isinstance(topics, list):
                    topics = ["How-to"]
            elif "category" in topic_data:
                topics = [topic_data.get("category", "How-to")]
            else:
                topics = ["How-to"]
            
            topic_tags = [TopicTag(topic) for topic in topics]
        except (ValueError, TypeError) as e:
            topic_tags = [TopicTag.HOW_TO]
        
        try:
            sentiment_label = sentiment_data.get("sentiment", "Neutral")
            # Normalize case and validate that the sentiment is one of our allowed values
            valid_sentiments = ["Neutral", "Curious", "Confused", "Frustrated", "Angry"]
            sentiment_label = sentiment_label.capitalize()  # Normalize case
            
            # Map similar sentiments to our valid categories
            sentiment_mapping = {
                "Concerned": "Confused",
                "Worried": "Confused", 
                "Annoyed": "Frustrated",
                "Upset": "Frustrated",
                "Irritated": "Frustrated",
                "Hostile": "Angry",
                "Furious": "Angry"
            }
            
            if sentiment_label in sentiment_mapping:
                sentiment_label = sentiment_mapping[sentiment_label]
            elif sentiment_label not in valid_sentiments:
                print(f"⚠️ Invalid sentiment '{sentiment_label}' returned, defaulting to 'Neutral'")
                sentiment_label = "Neutral"
            
            sentiment = Sentiment(sentiment_label)
        except (ValueError, TypeError) as e:
            sentiment = Sentiment.NEUTRAL
        
        # Calculate priority using enhanced mathematical scoring
        priority, priority_score, priority_reasoning = self._calculate_priority_score(topic_tags, sentiment, subject, body)
        
        # Calculate confidence based on score clarity
        confidence = min(0.95, 0.6 + (abs(priority_score - 4.5) / 10.0))
        
        # Simplified reasoning for speed
        reasoning = f"Topics: {', '.join([tag.value for tag in topic_tags])}; Sentiment: {sentiment.value}; Priority: {priority.value}"
        
        return ClassificationResult(
            topic_tags=topic_tags,
            sentiment=sentiment,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def classify_tickets_batch(self, tickets: List[Tuple[str, str]]) -> List[ClassificationResult]:
        """
        Classify multiple tickets efficiently with batching and rate limiting.
        """
        results = []
        batch_size = 3  # Process small batches for better speed
        
        for i in range(0, len(tickets), batch_size):
            batch = tickets[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(tickets) + batch_size - 1)//batch_size}")
            
            for subject, body in batch:
                try:
                    result = self.classify_ticket(subject, body)
                    results.append(result)
                except Exception as e:
                    print(f"Error classifying ticket: {e}")
                    results.append(ClassificationResult(
                        topic_tags=[TopicTag.HOW_TO],
                        sentiment=Sentiment.NEUTRAL,
                        priority=Priority.P2,
                        confidence=0.1,
                        reasoning=f"Batch classification failed: {str(e)}"
                    ))
            
            # Add delay between batches to respect rate limits
            if i + batch_size < len(tickets):
                import time
                time.sleep(2)  # Reduced delay for better speed
        
        return results
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from Grok API with error handling and caching."""
        # Check cache first
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        import time
        import random
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": "You are a ticket classifier. Respond with JSON only. No reasoning, no explanations, no additional text. Just the JSON object."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                result = response.choices[0].message.content
                # Cache the successful response
                self._cache_response(cache_key, result)
                return result
                
            except Exception as e:
                error_str = str(e)
                if "rate_limit_exceeded" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0.5, 1.5)
                        print(f"Rate limit hit, waiting {delay:.1f} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                        continue
                    else:
                        raise RuntimeError(f"Rate limit exceeded after {max_retries} attempts: {e}")
                else:
                    if attempt < max_retries - 1:
                        print(f"API error, retrying in {base_delay} seconds: {e}")
                        time.sleep(base_delay)
                        continue
                    else:
                        raise RuntimeError(f"API call failed after {max_retries} attempts: {e}")
        
        raise RuntimeError("Unexpected error in API call")
    
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache a response with size management."""
        # Simple LRU-style cache management
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entries (simple approach)
            keys_to_remove = list(self._cache.keys())[:len(self._cache) - self._cache_max_size + 1]
            for key in keys_to_remove:
                del self._cache[key]
        
        self._cache[cache_key] = response

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON response with error handling and cleaning."""
        try:
            # Clean the response more aggressively
            cleaned_response = response.strip()
            
            # Remove any markdown code blocks
            if '```json' in cleaned_response:
                start = cleaned_response.find('```json') + 7
                end = cleaned_response.find('```', start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            elif '```' in cleaned_response:
                start = cleaned_response.find('```') + 3
                end = cleaned_response.find('```', start)
                if end != -1:
                    cleaned_response = cleaned_response[start:end].strip()
            
            # Extract JSON content more robustly
            start_brace = cleaned_response.find('{')
            end_brace = cleaned_response.rfind('}')
            if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                cleaned_response = cleaned_response[start_brace:end_brace + 1]
            
            # More aggressive JSON cleaning
            import re
            # Remove all newlines and extra whitespace
            cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
            # Fix common JSON formatting issues
            cleaned_response = re.sub(r'\s*{\s*', '{', cleaned_response)
            cleaned_response = re.sub(r'\s*}\s*', '}', cleaned_response)
            cleaned_response = re.sub(r'\s*\[\s*', '[', cleaned_response)
            cleaned_response = re.sub(r'\s*\]\s*', ']', cleaned_response)
            cleaned_response = re.sub(r'\s*,\s*', ',', cleaned_response)
            cleaned_response = re.sub(r'\s*:\s*', ':', cleaned_response)
            cleaned_response = re.sub(r'"\s*', '"', cleaned_response)
            cleaned_response = re.sub(r'\s*"', '"', cleaned_response)
            
            # Try to parse the cleaned JSON
            parsed = json.loads(cleaned_response)
            
            # Clean up any keys that might still have whitespace issues
            if isinstance(parsed, dict):
                cleaned_dict = {}
                for key, value in parsed.items():
                    # Clean key names
                    clean_key = key.strip().replace('\n', '').replace('\r', '').replace('\t', '')
                    cleaned_dict[clean_key] = value
                return cleaned_dict
            
            return parsed
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse JSON response: {response}")
            print(f"Cleaned response: {cleaned_response if 'cleaned_response' in locals() else 'N/A'}")
            print(f"Error: {e}")
            # Return safe fallback
            return {"topics": ["How-to"], "reasoning": "Failed to parse response"}

    def classify_batch(self, tickets: List[Dict]) -> List[Dict]:
        """Classify a batch of tickets."""
        results = []
        for ticket in tickets:
            try:
                classification = self.classify_ticket(
                    ticket["subject"], 
                    ticket["body"]
                )
                
                result = {
                    "ticket": ticket,
                    "classification": {
                        "topic_tags": [tag.value for tag in classification.topic_tags],
                        "sentiment": classification.sentiment.value,
                        "priority": classification.priority.value,
                        "confidence": classification.confidence,
                        "reasoning": classification.reasoning
                    }
                }
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to classify ticket '{ticket.get('subject', 'Unknown')}': {e}")
                raise e
        
        return results
    
