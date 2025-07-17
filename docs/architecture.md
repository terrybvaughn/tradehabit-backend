# Architecture Overview

## Tech Stack

### Backend
- **Python 3.x** - Core runtime environment
- **Flask** - Web framework for REST API
- **Pandas & NumPy** - Data manipulation and statistical analysis
- **Flask-CORS** - Cross-origin resource sharing
- **Gunicorn** - Production WSGI server
- **Python-dateutil** - Advanced datetime handling
- **Werkzeug** - WSGI utilities and development server

### Frontend (External)
- **React 19** with TypeScript
- **Zustand** for state management
- **TanStack Query** for server state management
- **Modern CSS Modules** for styling

### Deployment
- **Backend**: Replit with auto-scaling
- **Frontend**: app.tradehab.it
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

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                     app.tradehab.it                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/JSON API
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Flask API Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   app.py        │  │   errors.py     │  │   CORS Config   │ │
│  │ 14+ endpoints   │  │ Error handling  │  │ Multi-origin    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Business Logic Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Analytics/    │  │   Parsing/      │  │   Models/       │ │
│  │ Mistake Analysis│  │ Data Processing │  │ Trade Objects   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Data Layer                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ In-Memory Store │  │ CSV Processing  │  │ Statistical     │ │
│  │ trade_objs[]    │  │ Pandas DataFrames│  │ Calculations    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
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

This architecture provides a robust foundation for behavioral trading analysis while maintaining simplicity and maintainability.