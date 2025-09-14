# Simplified Architecture Diagram

## Core System Flow

```mermaid
flowchart TD
    User[👤 User Query] --> Frontend[🖥️ React Frontend]
    Frontend --> API[⚡ FastAPI Backend]
    
    API --> Classifier[🎯 Sentiment Agent<br/>Claude-3.5-Sonnet]
    Classifier --> Decision{📋 Topic Classification}
    
    Decision -->|How-to, Product, API/SDK, SSO, Best practices| Tavily[🔍 Tavily Real-time Search]
    Decision -->|Connector, Lineage, Glossary, Other| Routing[📤 Route to Team]
    
    Tavily --> Docs[📖 docs.atlan.com]
    Tavily --> DevHub[⚙️ developer.atlan.com]
    
    Docs --> Answer[🤖 Claude Answer Generation]
    DevHub --> Answer
    
    Answer --> Format[🎨 Response Formatting]
    Routing --> Format
    
    Format --> Response[📋 Dual-Panel Response]
    Response --> User
    
    classDef user fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef frontend fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    classDef backend fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef ai fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:3px
    classDef decision fill:#f1f8e9,stroke:#33691e,stroke-width:3px
    
    class User user
    class Frontend frontend
    class API,Format,Response backend
    class Classifier,Answer ai
    class Tavily,Docs,DevHub external
    class Decision,Routing decision
```

## Component Responsibilities

### 🖥️ Frontend Layer
- **Interactive Agent UI**: Dual-panel interface for query and response
- **Ticket Dashboard**: Batch processing and statistics
- **Analytics Reports**: Sentiment insights and performance metrics

### ⚡ Backend Layer
- **FastAPI Server**: REST endpoints and async processing
- **CORS Middleware**: Cross-origin request handling
- **Response Formatting**: Clean answer separation from sources

### 🧠 AI Processing
- **Sentiment Agent**: Topic classification, sentiment analysis, priority scoring
- **Tavily System**: Orchestration and routing logic
- **Tavily RAG**: Real-time search and answer generation

### ☁️ External Services
- **Claude API**: Primary LLM for classification and answer generation
- **Tavily API**: Real-time web search and content extraction

### 📚 Knowledge Sources
- **docs.atlan.com**: Product documentation and user guides
- **developer.atlan.com**: API references and SDK documentation

## Data Flow Summary

1. **User Input** → React Frontend
2. **API Request** → FastAPI Backend
3. **Classification** → Sentiment Agent (Claude)
4. **Routing Decision** → Topic-based logic
5. **Search/Route** → Tavily Search OR Team Routing
6. **Answer Generation** → Claude (if Tavily used)
7. **Response Formatting** → Clean separation of content and sources
8. **UI Display** → Dual-panel interface

## Key Features

- ✅ **Smart Routing**: Only specific topics use Tavily search
- ✅ **Real-time Search**: Live documentation search with Tavily
- ✅ **Clean Formatting**: Sources separated from answers
- ✅ **Transparent UI**: Shows internal analysis and final response
- ✅ **Error Handling**: Graceful fallbacks for all failure modes
