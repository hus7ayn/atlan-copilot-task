#!/usr/bin/env python3
"""
FastAPI Backend for Atlan Customer Copilot
Provides sentiment analysis, classification, and RAG-based responses
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import sys
import tempfile
import shutil

# Add ai_pipeline to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_pipeline'))

from simple_tavily_system import get_simple_tavily_system, SimpleTavilySystem
from file_parser import file_parser

load_dotenv()

app = FastAPI(title="Atlan Customer Copilot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=False,  # Set to False when allowing all origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize components
simple_tavily_system = None

class TicketInput(BaseModel):
    text: str
    channel: Optional[str] = "web"

class TicketResponse(BaseModel):
    analysis: Dict[str, Any]
    final_response: str
    sources: Optional[List[str]] = None

class SentimentReportResponse(BaseModel):
    tickets: List[Dict[str, Any]]
    summary: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize the AI components on startup"""
    global simple_tavily_system
    
    try:
        print("🚀 Initializing Simple Tavily System...")
        
        # Check if required environment variables are present
        grok_key = os.getenv("GROK_API_KEY", "").strip()
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        print(f"🔍 Debug - GROK_API_KEY present: {bool(grok_key)}")
        print(f"🔍 Debug - TAVILY_API_KEY present: {bool(tavily_key)}")
        if grok_key:
            print(f"🔍 Debug - GROK_API_KEY starts with: {grok_key[:10]}...")
        if tavily_key:
            print(f"🔍 Debug - TAVILY_API_KEY starts with: {tavily_key[:10]}...")
        
        if not grok_key:
            print("⚠️ GROK_API_KEY not found - AI features will be limited")
        if not tavily_key:
            print("⚠️ TAVILY_API_KEY not found - real-time search will be limited")
        
        # Initialize even without API keys for basic functionality
        simple_tavily_system = SimpleTavilySystem()
        await simple_tavily_system.initialize()
        print("✅ Simple Tavily System initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        print("🔄 App will continue with limited functionality")
        # Don't raise the exception to prevent startup failure
        # The health check will indicate the system is not ready

# Root route removed - will be handled by catch-all route for React app

@app.get("/api/health")
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Check environment variables
        grok_key = os.getenv("GROK_API_KEY", "").strip()
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "simple_tavily_system": simple_tavily_system is not None and hasattr(simple_tavily_system, 'initialized') and simple_tavily_system.initialized,
            "grok_key_present": bool(grok_key),
            "tavily_key_present": bool(tavily_key),
            "grok_key_start": grok_key[:10] + "..." if grok_key else None,
            "tavily_key_start": tavily_key[:10] + "..." if tavily_key else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/test-grok")
async def test_grok():
    """Test Grok API directly"""
    try:
        import requests
        
        grok_key = os.getenv("GROK_API_KEY", "").strip()
        if not grok_key:
            return {"error": "GROK_API_KEY not found"}
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {grok_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gemma2-9b-it",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "response": result["choices"][0]["message"]["content"],
                "status_code": response.status_code
            }
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.post("/api/tickets", response_model=TicketResponse)
async def process_ticket(ticket: TicketInput):
    """
    Process a new ticket with classification and RAG-based response
    """
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily System not initialized")
    
    try:
        # Check if sentiment agent is available
        if not simple_tavily_system.sentiment_agent:
            raise HTTPException(status_code=500, detail="Sentiment Agent not initialized - check API keys")
        
        # Step 1: Classify the ticket
        print(f"🔍 Classifying ticket: {ticket.text[:50]}...")
        classification = simple_tavily_system.sentiment_agent.classify_ticket("", ticket.text)
        
        # Prepare analysis data
        analysis = {
            "topic_tags": [tag.value for tag in classification.topic_tags],
            "sentiment": classification.sentiment.value,
            "priority": classification.priority.value,
            "confidence": classification.confidence,
            "reasoning": classification.reasoning,
            "evidence": {
                "topic_confidence": classification.confidence,
                "sentiment_confidence": classification.confidence,
                "priority_score": classification.confidence
            }
        }
        
        # Step 2: Determine if we should use RAG
        rag_topics = {"How-to", "Product", "Best practices", "API/SDK", "SSO"}
        topic_tags = {tag.value for tag in classification.topic_tags}
        
        if topic_tags.intersection(rag_topics):
            # Use RAG system
            print(f"🤖 Using RAG for topics: {topic_tags.intersection(rag_topics)}")
            final_response, sources = await rag_system.get_answer(ticket.text, classification.topic_tags)
            
            return TicketResponse(
                analysis=analysis,
                final_response=final_response,
                sources=sources
            )
        else:
            # Route to appropriate team
            primary_topic = classification.topic_tags[0].value if classification.topic_tags else "Other"
            routing_message = f"This ticket has been classified as a '{primary_topic}' issue and routed to the appropriate team."
            
            return TicketResponse(
                analysis=analysis,
                final_response=routing_message,
                sources=None
            )
            
    except Exception as e:
        print(f"❌ Error processing ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")

@app.get("/api/tickets")
async def get_tickets():
    """
    Get all tickets with classification from sample_tickets.json
    """
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily System not initialized")
    
    try:
        with open('sample_tickets.json', 'r') as f:
            tickets_data = json.load(f)
        
        print(f"📊 Processing {len(tickets_data)} tickets for classification...")
        
        # Classify all tickets
        classified_tickets = []
        for ticket in tickets_data:
            try:
                classification = simple_tavily_system.sentiment_agent.classify_ticket(
                    ticket.get('subject', ''),
                    ticket.get('body', '')
                )
                
                classified_ticket = {
                    "id": ticket.get('id', ''),
                    "subject": ticket.get('subject', ''),
                    "body": ticket.get('body', ''),
                    "customer_email": ticket.get('customer_email', ''),
                    "created_at": ticket.get('created_at', ''),
                    "classification": {
                        "topic_tags": [tag.value for tag in classification.topic_tags],
                        "sentiment": classification.sentiment.value,
                        "priority": classification.priority.value,
                        "confidence": classification.confidence,
                        "reasoning": classification.reasoning
                    }
                }
                classified_tickets.append(classified_ticket)
                
            except Exception as e:
                print(f"⚠️ Error classifying ticket {ticket.get('id', 'unknown')}: {e}")
                # Add ticket with error classification
                classified_ticket = {
                    "id": ticket.get('id', ''),
                    "subject": ticket.get('subject', ''),
                    "body": ticket.get('body', ''),
                    "customer_email": ticket.get('customer_email', ''),
                    "created_at": ticket.get('created_at', ''),
                    "classification": {
                        "topic_tags": ["How-to"],
                        "sentiment": "Neutral",
                        "priority": "P2 (Low)",
                        "confidence": 0.0,
                        "reasoning": f"Classification failed: {str(e)}"
                    }
                }
                classified_tickets.append(classified_ticket)
        
        return {"tickets": classified_tickets}
        
    except Exception as e:
        print(f"❌ Error loading and classifying tickets: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading tickets: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """
    Get basic statistics about the system
    """
    try:
        with open('sample_tickets.json', 'r') as f:
            tickets_data = json.load(f)
        
        return {
            "total_tickets": len(tickets_data),
            "system_status": "healthy",
            "simple_tavily_system_ready": simple_tavily_system is not None and simple_tavily_system.initialized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading stats: {str(e)}")

@app.get("/api/sentiment-report", response_model=SentimentReportResponse)
async def get_sentiment_report():
    """
    Generate sentiment analysis report for all tickets in sample_tickets.json
    """
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily System not initialized")
    
    try:
        # Load sample tickets
        with open('sample_tickets.json', 'r') as f:
            tickets_data = json.load(f)
        
        print(f"📊 Processing {len(tickets_data)} tickets for sentiment report...")
        
        # Classify all tickets
        classified_tickets = []
        for ticket in tickets_data:
            try:
                classification = simple_tavily_system.sentiment_agent.classify_ticket(
                    ticket.get('subject', ''),
                    ticket.get('body', '')
                )
                
                classified_ticket = {
                    "id": ticket.get('id', ''),
                    "subject": ticket.get('subject', ''),
                    "body": ticket.get('body', ''),
                    "customer_email": ticket.get('customer_email', ''),
                    "created_at": ticket.get('created_at', ''),
                    "classification": {
                        "topic_tags": [tag.value for tag in classification.topic_tags],
                        "sentiment": classification.sentiment.value,
                        "priority": classification.priority.value,
                        "confidence": classification.confidence,
                        "reasoning": classification.reasoning
                    }
                }
                classified_tickets.append(classified_ticket)
                
            except Exception as e:
                print(f"⚠️ Error classifying ticket {ticket.get('id', 'unknown')}: {e}")
                # Add ticket with error classification
                classified_ticket = {
                    "id": ticket.get('id', ''),
                    "subject": ticket.get('subject', ''),
                    "body": ticket.get('body', ''),
                    "customer_email": ticket.get('customer_email', ''),
                    "created_at": ticket.get('created_at', ''),
                    "classification": {
                        "topic_tags": ["How-to"],
                        "sentiment": "Neutral",
                        "priority": "P2 (Low)",
                        "confidence": 0.0,
                        "reasoning": f"Classification failed: {str(e)}"
                    }
                }
                classified_tickets.append(classified_ticket)
        
        # Generate summary statistics
        summary = generate_summary_statistics(classified_tickets)
        
        return SentimentReportResponse(
            tickets=classified_tickets,
            summary=summary
        )
        
    except Exception as e:
        print(f"❌ Error generating sentiment report: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating sentiment report: {str(e)}")

def generate_summary_statistics(tickets: List[Dict]) -> Dict[str, Any]:
    """Generate summary statistics from classified tickets"""
    
    # Count by sentiment
    sentiment_counts = {}
    topic_counts = {}
    priority_counts = {}
    confidence_scores = []
    
    for ticket in tickets:
        classification = ticket.get('classification', {})
        
        # Sentiment counts
        sentiment = classification.get('sentiment', 'Unknown')
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Topic counts
        topics = classification.get('topic_tags', [])
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Priority counts
        priority = classification.get('priority', 'Unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Confidence scores
        confidence = classification.get('confidence', 0)
        confidence_scores.append(confidence)
    
    # Calculate average confidence
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    return {
        "total_tickets": len(tickets),
        "sentiment_distribution": sentiment_counts,
        "topic_distribution": topic_counts,
        "priority_distribution": priority_counts,
        "average_confidence": round(avg_confidence, 3),
        "high_confidence_tickets": len([c for c in confidence_scores if c > 0.8]),
        "low_confidence_tickets": len([c for c in confidence_scores if c < 0.5])
    }

@app.post("/api/interactive-agent")
async def process_interactive_ticket(ticket: TicketInput):
    """
    Process a ticket through the simple Tavily system with dual-panel analysis
    Shows internal analysis (classification) and final response (Tavily or routing)
    """
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily System not initialized")
    
    try:
        print(f"🔍 Processing interactive ticket with Simple Tavily System: {ticket.text[:50]}...")
        
        # Process ticket with simple Tavily system
        tavily_response = await simple_tavily_system.process_ticket(ticket.text)
        
        # Get internal analysis (classification details)
        analysis = await simple_tavily_system.analyze_ticket(ticket.text)
        
        # Prepare analysis data for left panel (Internal Analysis View)
        internal_analysis = {
            "topic_tags": analysis.topic_tags,
            "sentiment": analysis.sentiment,
            "priority": analysis.priority,
            "confidence": analysis.confidence,
            "reasoning": analysis.reasoning,
                "classification_time": datetime.now().isoformat()
        }
        
        # Prepare final response data for right panel (Final Response View)
        final_response_data = {
            "answer": tavily_response.answer,
            "sources": tavily_response.sources,
            "confidence": tavily_response.confidence,
            "is_tavily_used": tavily_response.is_tavily_used,
            "routing_message": tavily_response.routing_message
        }
        
        return {
            "internal_analysis": internal_analysis,
            "final_response": final_response_data,
            "processing_method": "tavily" if tavily_response.is_tavily_used else "routed"
        }
        
    except Exception as e:
        print(f"❌ Error processing interactive ticket: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing ticket: {str(e)}")

@app.post("/api/realtime-search")
async def realtime_search(ticket: TicketInput):
    """
    Perform real-time search using Tavily API only
    Bypasses static RAG for immediate real-time results
    """
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily system not initialized")
    
    try:
        print(f"🔍 Performing real-time search: {ticket.text[:50]}...")
        
        # Process ticket with Tavily system
        tavily_response = await simple_tavily_system.process_ticket(ticket.text)
        
        # Get internal analysis
        analysis = await simple_tavily_system.analyze_ticket(ticket.text)
        
        return {
            "internal_analysis": {
                "topic_tags": analysis.topic_tags,
                "sentiment": analysis.sentiment,
                "priority": analysis.priority,
                "confidence": analysis.confidence,
                "reasoning": analysis.reasoning
            },
            "final_response": {
                "answer": tavily_response.answer,
                "sources": tavily_response.sources,
                "confidence": tavily_response.confidence,
                "is_tavily_used": tavily_response.is_tavily_used,
                "routing_message": tavily_response.routing_message
            },
            "processing_method": "tavily" if tavily_response.is_tavily_used else "routed"
        }
        
    except Exception as e:
        print(f"❌ Error in real-time search: {e}")
        raise HTTPException(status_code=500, detail=f"Error in real-time search: {str(e)}")

@app.get("/api/rag-stats")
async def get_rag_stats():
    """Get simple Tavily system statistics"""
    if not simple_tavily_system:
        raise HTTPException(status_code=500, detail="Simple Tavily system not initialized")
    
    try:
        stats = await simple_tavily_system.get_system_stats()
        return {
            "success": True,
            "stats": stats,
            "system_type": "simple_tavily_only"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Tavily stats: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and parse a file to extract tickets
    Supports: PDF, DOCX, TXT, CSV, JSON, HTML, MD, LOG, XML, YAML
    """
    try:
        print(f"📁 Processing uploaded file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Parse the file
        parse_result = file_parser.parse_file(file.filename, file_content)
        
        if not parse_result['success']:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": parse_result['error'],
                    "supported_formats": parse_result.get('supported_formats', [])
                }
            )
        
        # Extract tickets from the parsed content
        tickets = file_parser.extract_tickets_from_content(parse_result['content'])
        
        # Process each ticket with the AI system
        processed_tickets = []
        for ticket in tickets:
            try:
                # Classify the ticket
                analysis = simple_tavily_system.sentiment_agent.classify_ticket(
                    ticket['subject'], 
                    ticket['body']
                )
                
                # Process with Tavily system
                tavily_response = await simple_tavily_system.process_ticket(ticket['body'])
                
                processed_ticket = {
                    "id": ticket['id'],
                    "subject": ticket['subject'],
                    "body": ticket['body'],
                    "created_at": ticket['created_at'],
                    "customer_email": ticket['customer_email'],
                    "classification": {
                        "topic_tags": [tag.value for tag in analysis.topic_tags],
                        "sentiment": analysis.sentiment.value,
                        "priority": analysis.priority.value,
                        "confidence": analysis.confidence,
                        "reasoning": analysis.reasoning
                    },
                    "tavily_response": {
                        "answer": tavily_response.answer,
                        "sources": tavily_response.sources,
                        "confidence": tavily_response.confidence,
                        "is_tavily_used": tavily_response.is_tavily_used,
                        "routing_message": tavily_response.routing_message
                    }
                }
                
                processed_tickets.append(processed_ticket)
                
            except Exception as e:
                print(f"⚠️ Error processing ticket {ticket['id']}: {e}")
                # Add ticket with error info
                processed_tickets.append({
                    "id": ticket['id'],
                    "subject": ticket['subject'],
                    "body": ticket['body'],
                    "created_at": ticket['created_at'],
                    "customer_email": ticket['customer_email'],
                    "error": f"Processing error: {str(e)}"
                })
        
        return {
            "success": True,
            "file_info": {
                "filename": file.filename,
                "file_type": parse_result['file_type'],
                "word_count": parse_result['word_count'],
                "char_count": parse_result['char_count']
            },
            "tickets_found": len(tickets),
            "tickets_processed": len(processed_tickets),
            "tickets": processed_tickets
        }
        
    except Exception as e:
        print(f"❌ Error processing uploaded file: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error processing file: {str(e)}"
            }
        )

@app.post("/api/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Upload and parse multiple files to extract tickets
    """
    try:
        print(f"📁 Processing {len(files)} uploaded files")
        
        all_tickets = []
        file_results = []
        
        for file in files:
            try:
                # Read file content
                file_content = await file.read()
                
                # Parse the file
                parse_result = file_parser.parse_file(file.filename, file_content)
                
                if not parse_result['success']:
                    file_results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": parse_result['error']
                    })
                    continue
                
                # Extract tickets from the parsed content
                tickets = file_parser.extract_tickets_from_content(parse_result['content'])
                
                # Process each ticket with the AI system
                processed_tickets = []
                for ticket in tickets:
                    try:
                        # Classify the ticket
                        analysis = simple_tavily_system.sentiment_agent.classify_ticket(
                            ticket['subject'], 
                            ticket['body']
                        )
                        
                        # Process with Tavily system
                        tavily_response = await simple_tavily_system.process_ticket(ticket['body'])
                        
                        processed_ticket = {
                            "id": f"{file.filename}-{ticket['id']}",
                            "subject": ticket['subject'],
                            "body": ticket['body'],
                            "created_at": ticket['created_at'],
                            "customer_email": ticket['customer_email'],
                            "source_file": file.filename,
                            "classification": {
                                "topic_tags": [tag.value for tag in analysis.topic_tags],
                                "sentiment": analysis.sentiment.value,
                                "priority": analysis.priority.value,
                                "confidence": analysis.confidence,
                                "reasoning": analysis.reasoning
                            },
                            "tavily_response": {
                                "answer": tavily_response.answer,
                                "sources": tavily_response.sources,
                                "confidence": tavily_response.confidence,
                                "is_tavily_used": tavily_response.is_tavily_used,
                                "routing_message": tavily_response.routing_message
                            }
                        }
                        
                        processed_tickets.append(processed_ticket)
                        all_tickets.append(processed_ticket)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing ticket {ticket['id']} from {file.filename}: {e}")
                        # Add ticket with error info
                        processed_tickets.append({
                            "id": f"{file.filename}-{ticket['id']}",
                            "subject": ticket['subject'],
                            "body": ticket['body'],
                            "created_at": ticket['created_at'],
                            "customer_email": ticket['customer_email'],
                            "source_file": file.filename,
                            "error": f"Processing error: {str(e)}"
                        })
                
                file_results.append({
                    "filename": file.filename,
                    "success": True,
                    "file_type": parse_result['file_type'],
                    "word_count": parse_result['word_count'],
                    "char_count": parse_result['char_count'],
                    "tickets_found": len(tickets),
                    "tickets_processed": len(processed_tickets)
                })
                
            except Exception as e:
                print(f"❌ Error processing file {file.filename}: {e}")
                file_results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Error processing file: {str(e)}"
                })
        
        return {
            "success": True,
            "files_processed": len(files),
            "files_successful": len([f for f in file_results if f['success']]),
            "total_tickets": len(all_tickets),
            "file_results": file_results,
            "tickets": all_tickets
        }
        
    except Exception as e:
        print(f"❌ Error processing multiple files: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error processing files: {str(e)}"
            }
        )

@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "success": True,
        "supported_formats": list(file_parser.supported_formats.keys()),
        "formats_info": {
            ".pdf": "PDF documents",
            ".docx": "Microsoft Word documents",
            ".doc": "Microsoft Word documents (legacy)",
            ".txt": "Plain text files",
            ".csv": "Comma-separated values",
            ".json": "JSON data files",
            ".html": "HTML web pages",
            ".htm": "HTML web pages",
            ".md": "Markdown documents",
            ".log": "Log files",
            ".xml": "XML documents",
            ".yaml": "YAML configuration files",
            ".yml": "YAML configuration files"
        }
    }

# Serve React app in production
if os.path.exists("client/build"):
    app.mount("/static", StaticFiles(directory="client/build/static"), name="static")
    
    @app.get("/{catch_all:path}")
    async def serve_react_app(catch_all: str):
        """Serve React app for all non-API routes"""
        # Skip API routes
        if catch_all.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        from fastapi.responses import FileResponse
        return FileResponse("client/build/index.html")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Debug: Show all environment variables
    print("🔍 Environment variables:")
    for key, value in os.environ.items():
        if 'PORT' in key.upper():
            print(f"  {key}={value}")
    
    # Get port with fallback
    port_str = os.getenv("PORT", "8000")
    print(f"🔧 PORT environment variable: '{port_str}'")
    
    try:
        port = int(port_str)
        print(f"🚀 Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ValueError as e:
        print(f"❌ Error parsing PORT '{port_str}': {e}")
        print("🔄 Using default port 8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)
