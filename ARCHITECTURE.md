# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ATLAN CUSTOMER COPILOT                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   FastAPI       │    │   AI Pipeline   │
│                 │    │   Backend       │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Interactive │ │    │ │ REST API    │ │    │ │ Sentiment   │ │
│ │ Agent       │ │◄───┤ │ Endpoints   │ │◄───┤ │ Agent       │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Dashboard   │ │    │ │ Main App    │ │    │ │ Tavily RAG  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ │ Integration│ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ └─────────────┘ │
│ │ Reports     │ │    │ │ Ticket      │ │    │ ┌─────────────┐ │
│ └─────────────┘ │    │ │ Processing  │ │    │ │ Simple      │ │
└─────────────────┘    │ └─────────────┘ │    │ │ Tavily      │ │
                       └─────────────────┘    │ │ System      │ │
                                              │ └─────────────┘ │
                                              └─────────────────┘
                                                       │
                       ┌───────────────────────────────┼───────────────────────────────┐
                       │                               │                               │
              ┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
              │   External  │                 │   External  │                 │   Data      │
              │   Services  │                 │   Services  │                 │   Storage   │
              │             │                 │             │                 │             │
              │ ┌─────────┐ │                 │ ┌─────────┐ │                 │ ┌─────────┐ │
              │ │ Claude  │ │                 │ │ Tavily  │ │                 │ │ ChromaDB│ │
              │ │ API     │ │                 │ │ API     │ │                 │ │ Vector  │ │
              │ └─────────┘ │                 │ └─────────┘ │                 │ │ Store   │ │
              │             │                 │             │                 │ └─────────┘ │
              │             │                 │ ┌─────────┐ │                 │ ┌─────────┐ │
              │             │                 │ │ Atlan   │ │                 │ │ Sample  │ │
              │             │                 │ │ Docs    │ │                 │ │ Tickets │ │
              │             │                 │ │ Site    │ │                 │ │ JSON    │ │
              │             │                 │ └─────────┘ │                 │ └─────────┘ │
              │             │                 │             │                 │             │
              │             │                 │ ┌─────────┐ │                 │             │
              │             │                 │ │ Dev Hub │ │                 │             │
              │             │                 │ │ Site    │ │                 │             │
              │             │                 │ └─────────┘ │                 │             │
              └─────────────┘                 └─────────────┘                 └─────────────┘
```

## Data Flow Sequence

```
1. USER INPUT
   └─> React UI (Interactive Agent)

2. API REQUEST
   └─> FastAPI Backend (/api/interactive-agent)

3. TICKET CLASSIFICATION
   └─> Sentiment Agent
       └─> Claude API (Topic, Sentiment, Priority)

4. ROUTING DECISION
   └─> Simple Tavily System
       ├─> If Topic ∈ {How-to, Product, Best practices, API/SDK, SSO}
       │   └─> Use Tavily Search
       └─> Else
           └─> Route to Team

5. SEARCH & ANSWER GENERATION (if Tavily)
   └─> Tavily RAG Integration
       ├─> Tavily API → Search Documentation
       ├─> Claude API → Generate Answer
       └─> Clean & Format Response

6. RESPONSE FORMATTING
   └─> Structured Response
       ├─> Clean Answer (no source links)
       └─> Separate Sources Section

7. UI DISPLAY
   └─> Dual-Panel Interface
       ├─> Left: Internal Analysis
       └─> Right: Final Response + Sources
```

## Component Responsibilities

### Frontend (React)
- **Interactive Agent UI**: Query input and response display
- **Ticket Dashboard**: Batch ticket management and statistics
- **Sentiment Reports**: Analytics and insights

### Backend (FastAPI)
- **REST API**: HTTP endpoints for frontend communication
- **Main Application**: Request routing and orchestration
- **CORS Handling**: Cross-origin request management

### AI Pipeline
- **Sentiment Agent**: 
  - Topic classification (10 categories)
  - Sentiment analysis (5 levels)
  - Priority assignment (6-factor scoring)
- **Tavily RAG Integration**:
  - Real-time documentation search
  - Answer generation with Claude
  - Source extraction and formatting
- **Simple Tavily System**:
  - Main orchestration layer
  - Routing logic implementation
  - Response coordination

### External Services
- **Claude API**: LLM for classification and answer generation
- **Tavily API**: Real-time web search and content extraction
- **Atlan Documentation**: docs.atlan.com (product docs)
- **Developer Hub**: developer.atlan.com (API/SDK docs)

### Data Storage
- **ChromaDB**: Vector database for semantic search
- **Sample Tickets**: JSON file with test data

## Key Design Patterns

1. **Hybrid RAG**: Combines static (ChromaDB) and dynamic (Tavily) search
2. **Strict Routing**: Topic-based decision making for resource allocation
3. **Prompt Engineering**: Optimized prompts for better search and answer quality
4. **Async Processing**: Non-blocking I/O for better performance
5. **Separation of Concerns**: Clear boundaries between classification, search, and formatting
