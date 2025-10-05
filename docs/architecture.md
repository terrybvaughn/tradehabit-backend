# Architecture Overview

## Tech Stack

### Core Backend
- **Python 3.x** - Core runtime environment
- **Flask** - Web framework for REST API
- **Pandas & NumPy** - Data manipulation and statistical analysis
- **Flask-CORS** - Cross-origin resource sharing
- **Gunicorn** - Production WSGI server
- **Python-dateutil** - Advanced datetime handling
- **Werkzeug** - WSGI utilities and development server

### Mentor (AI Coach)
- **Backend**: Flask tool runner (Python 3.9+) serving analytics fixtures
- **Frontend**: Next.js 14.2.5 + React 18.2.0 + TypeScript 5.4.5
- **AI Provider**: OpenAI Assistants API (GPT-4)
- **Prompt Corpus**: 13 markdown/JSON files defining persona, knowledge, and templates

### Frontend (External)
- **React 19** with TypeScript
- **Zustand** for state management
- **TanStack Query** for server state management
- **Modern CSS Modules** for styling

### Deployment
- **Core Backend**: Replit with auto-scaling
- **Frontend**: app.tradehab.it
- **Mentor**: Development only (separate ports 3000/5000)
- **WSGI Configuration**: Gunicorn with Procfile

## High-Level Application Design

### Architecture Pattern
The application follows a **three-tier architecture**:

1. **Presentation Layer**: React frontend (separate repository)
2. **Business Logic Layer**: Flask API with behavioral analysis modules
3. **Data Layer**: In-memory data processing with CSV file uploads

### Core Design Principles

#### 1. **Behavioral Analytics First**
- Primary focus on identifying trading mistakes rather than just performance metrics
- Statistical approach to mistake detection using configurable thresholds
- Prioritized insights using decision-tree logic

#### 2. **Stateless API Design**
- RESTful endpoints with JSON responses
- In-memory data storage for session-based analysis
- No persistent database - data uploaded per session

#### 3. **Modular Analysis Pipeline**
- Separate analyzer modules for different mistake types
- Orchestrated analysis through `mistake_analyzer.py`
- Mutation-based approach where analyzers modify Trade objects directly

#### 4. **Real-time Configuration**
- User-adjustable analysis thresholds via `/api/settings`
- Query parameter overrides for individual requests
- Dynamic re-analysis without requiring data re-upload

## System Architecture Diagram

### Core Analytics System
```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                     app.tradehab.it                             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/JSON API
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Flask API Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   app.py        │  │   errors.py     │  │   CORS Config   │  │
│  │ 14+ endpoints   │  │ Error handling  │  │ Multi-origin    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Business Logic Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   Analytics/    │  │   Parsing/      │  │   Models/       │  │
│  │ Mistake Analysis│  │ Data Processing │  │ Trade Objects   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Data Layer                                    │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ In-Memory Store │  │ CSV Processing   │  │ Statistical     │ │
│  │ trade_objs[]    │  │ Pandas DataFrames│  │ Calculations    │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### TradeHabit Mentor System (Separate)
```
┌─────────────────────────────────────────────────────────────────┐
│                 Mentor Chat UI (Next.js)                        │
│                    localhost:3000                               │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │  Chat.tsx      │  │  /api/chat     │  │  runAssistant.ts │   │
│  └────────────────┘  └────────────────┘  └──────────────────┘   │
└──────────────┬───────────────────────────────┬──────────────────┘
               │                               │
               │ OpenAI Assistants API         │ Tool Runner API
               │                               │
┌──────────────▼──────────────┐   ┌───────────▼───────────────────┐
│   OpenAI Platform           │   │   Tool Runner (Flask)         │
│   ┌──────────────────────┐  │   │      localhost:5000           │
│   │  Assistant (GPT-4.1) │  │   │  ┌─────────────────────────┐  │
│   │  - System Prompt     │  │   │  │ 8 Endpoints:            │  │
│   │  - 4 Function Tools  │  │   │  │ - get_summary_data      │  │
│   │  - Thread Management │  │   │  │ - get_endpoint_data     │  │
│   └──────────────────────┘  │   │  │ - filter_trades         │  │
└─────────────────────────────┘   │  │ - filter_losses         │  │
                                  │  └─────────────────────────┘  │
                                  │  ┌─────────────────────────┐  │
                                  │  │ JSON Fixtures (9 files) │  │
                                  │  │ mentor/tool_runner/     │  │
                                  │  │      static/            │  │
                                  │  └─────────────────────────┘  │
                                  └───────────────────────────────┘

Prompt Corpus (13 files in mentor/prompts/):
├── assistant/system_instructions/
├── persona/ (3 files)
├── knowledge_base/ (4 files)
├── templates/ (3 files)
└── conversation_starters/ (2 files)
```

## Data Flow Architecture

### 1. **Data Ingestion Flow**
```
CSV Upload → Validation → Parsing → Normalization → Trade Construction
```

### 2. **Analysis Flow**
```
Trade Objects → Mistake Detection → Statistical Analysis → Insights Generation
```

### 3. **API Response Flow**
```
Request → Analysis → JSON Serialization → CORS Headers → Response
```

## Key Architectural Decisions

### 1. **In-Memory Data Storage**
- **Decision**: Store all data in Python lists/dictionaries during session
- **Rationale**: Simplifies deployment, reduces complexity, suitable for session-based analysis
- **Trade-offs**: Data lost on restart, memory usage scales with data size

### 2. **Mutation-Based Analysis**
- **Decision**: Analyzer modules modify Trade objects directly
- **Rationale**: Efficient memory usage, clear data flow, simple state management
- **Trade-offs**: Potential side effects, requires careful ordering

### 3. **Statistical Threshold Configuration**
- **Decision**: User-configurable sigma multipliers and thresholds
- **Rationale**: Allows personalization, accommodates different trading styles
- **Implementation**: Global `THRESHOLDS` dict with API endpoints

### 4. **Modular Analyzer Design**
- **Decision**: Separate modules for each mistake type
- **Rationale**: Maintainability, testability, extensibility
- **Structure**: Common interface with specialized logic

### 5. **Flask over FastAPI**
- **Decision**: Use Flask for API framework
- **Rationale**: Simplicity, proven stability, sufficient performance for use case
- **Trade-offs**: Less automatic documentation, fewer built-in features

## Error Handling Strategy

### 1. **Centralized Error Handling**
- `errors.py` provides consistent JSON error responses
- HTTP exception handling for all endpoints
- Graceful degradation for data quality issues

### 2. **Validation Layers**
- File validation (size, format)
- Data schema validation
- Statistical calculation error handling

### 3. **User-Friendly Error Messages**
- Maps internal column names to original CSV headers
- Provides specific missing column information
- Graceful handling of malformed data

## Scalability Considerations

### Current Architecture Limitations
- **Memory Usage**: All data stored in memory during session
- **Single-User**: No user authentication or data isolation
- **No Persistence**: Data lost on application restart

### Potential Scaling Approaches
1. **Database Integration**: PostgreSQL for persistent storage
2. **User Authentication**: JWT-based session management
3. **Caching Layer**: Redis for computed analysis results
4. **Microservices**: Split analysis modules into separate services

## Security Architecture

### Current Security Measures
- **File Upload Validation**: Size limits, format restrictions
- **CORS Configuration**: Restricted origins list
- **Input Validation**: CSV schema validation
- **Error Handling**: No sensitive data exposure

### Security Considerations
- All data processing is read-only
- No database connections or external API calls
- Stateless design reduces attack surface
- No user authentication currently implemented

## Performance Characteristics

### Computational Complexity
- **Trade Detection**: O(n) where n = number of orders
- **Statistical Analysis**: O(n) for each analyzer
- **Insight Generation**: O(n) with decision tree logic

### Memory Usage
- **Linear Growth**: With number of trades and orders
- **Efficient Processing**: Pandas operations for bulk calculations
- **Minimal Overhead**: Simple data structures

---

## TradeHabit Mentor Architecture

### Overview

TradeHabit Mentor operates as a **separate prototype system** alongside the core analytics backend. It provides AI-powered coaching through conversational analysis of trading behavior.

### Architectural Approach

#### 1. **Decoupled Design**
- **Decision**: Separate standalone system during development
- **Rationale**: Enables rapid iteration without affecting core analytics; validates product-market fit before integration
- **Trade-offs**: Duplicate data fixtures; no unified authentication; separate deployment

#### 2. **Orchestrated AI Pattern**
- **Decision**: Use OpenAI Assistants API with function calling
- **Rationale**: Leverages managed threads, automatic retries, and state persistence
- **Implementation**: 4 function tools for data access; 13-file prompt corpus for behavior

#### 3. **Static Data Fixtures**
- **Decision**: Serve analytics from local JSON files
- **Rationale**: Development simplicity; decouples from live backend during prototyping
- **Trade-offs**: No real-time data; manual fixture updates required

#### 4. **Comprehensive Prompt Engineering**
- **Decision**: 13-file prompt corpus with strict routing rules
- **Rationale**: Ensures consistent, accurate responses; enforces terminology; prevents hallucination
- **Structure**: Persona → Knowledge Base → Templates → Application Logic

### Mentor Data Flow

```
1. User Message → Chat UI
2. Chat UI → OpenAI Assistants API (create message + run)
3. Assistant → Function Call Request (get_summary_data, filter_trades, etc.)
4. Chat UI → Tool Runner (fetch data from JSON fixture)
5. Tool Runner → JSON Response
6. Chat UI → OpenAI Assistants API (submit tool outputs)
7. Assistant → Generate Response (using prompt corpus + data)
8. OpenAI → Chat UI → User
```

### Key Mentor Components

#### **Tool Runner** (`mentor/tool_runner/tool_runner.py`)
- Flask service serving 8 REST endpoints
- In-memory caching of JSON fixtures
- Pagination, filtering, and sorting support
- Automatic endpoint discovery from available fixtures

#### **Assistant Orchestrator** (`mentor/chat-ui/src/lib/runAssistant.ts`)
- Manages OpenAI Assistant runs and threads
- Executes function calls via Tool Runner
- Retry logic for rate limiting (429 errors)
- Error handling and graceful degradation

#### **Prompt Corpus** (`mentor/prompts/`)
- **System Instructions**: Routing logic, tool policies, response rules
- **Persona**: Core personality, conversation guidelines, domain expertise
- **Knowledge Base**: Metric definitions, analytics explanations, TradeHabit functionality
- **Templates**: Response formats, explanation patterns, conversation starters

### Integration Considerations

#### Current State
- ⚠️ **Development Prototype**: Not production-ready
- 🔧 **No Backend Integration**: Operates independently from core API
- 📁 **Static Fixtures**: Data manually exported to JSON files
- 🚫 **No Multi-Tenancy**: All users see same fixture data

#### Future Production Architecture
```
┌────────────────────────────────────────────────────────────────┐
│                    Main TradeHabit Backend                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /api/mentor/*  Mentor Endpoints (Unified API)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Mentor Service Layer                                    │  │
│  │  - Real-time analytics data (from database)              │  │
│  │  - User authentication & multi-tenancy                   │  │
│  │  - OpenAI integration with user context                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```


### Security Considerations

#### Current Implementation
- **No Authentication**: Tool runner has CORS enabled for all origins
- **Environment Secrets**: API keys stored in `.env.local`
- **Read-Only Data**: Tool runner serves static fixtures only
- **No User Data**: Fixtures are synthetic test data

#### Production Requirements
- JWT-based authentication for API access
- User-specific data isolation (multi-tenancy)
- Rate limiting per user/session
- Audit logging for AI interactions
- Input sanitization for tool runner queries

### Documentation

For complete Mentor technical documentation, see:
- **[`docs/mentor.md`](./mentor.md)** - Complete technical reference
- **[`mentor/prompts/prompt_loading_order.md`](../mentor/prompts/prompt_loading_order.md)** - Prompt corpus guide

---

This architecture provides a robust foundation for behavioral trading analysis while maintaining simplicity and maintainability, with TradeHabit Mentor adding AI-powered coaching capabilities.