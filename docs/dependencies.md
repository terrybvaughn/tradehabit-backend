# Dependencies Analysis

## Overview

TradeHabit has two distinct dependency stacks:
1. **Core Backend** - Python/Flask analytics API (documented below)
2. **Mentor** - AI coaching system with separate frontend and tool runner (see [Mentor Dependencies](#mentor-dependencies))

---

## Core Backend Dependencies

### Production Dependencies

#### **Flask (>= 3.0)**
- **Purpose**: Web framework providing the REST API foundation
- **Usage**: 
  - Route handling for 14+ API endpoints
  - Request/response processing
  - JSON serialization
  - HTTP method routing
- **Key Features Used**:
  - `@app.route()` decorators for endpoint definitions
  - `request.files` for file upload handling
  - `request.args` for query parameter processing
  - `jsonify()` for JSON response formatting
  - `abort()` for error handling

#### **Flask-CORS (>= 4.0)**
- **Purpose**: Cross-Origin Resource Sharing support
- **Usage**: Enables frontend-backend communication across different origins
- **Configuration**:
  ```python
  CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})
  ```
- **Supported Origins**:
  - Local development servers (localhost:5173)
  - Production frontend (app.tradehab.it)
  - Replit deployment environment

#### **Pandas (>= 2.0)**
- **Purpose**: Data manipulation and analysis library
- **Usage**: 
  - CSV file processing and validation
  - DataFrame operations for order data
  - Statistical calculations and aggregations
  - Data type conversions and cleaning
- **Key Operations**:
  - `pd.read_csv()` for file loading
  - DataFrame filtering and grouping
  - Column renaming and normalization
  - Timestamp processing

#### **NumPy (>= 1.24)**
- **Purpose**: Numerical computing foundation (implicit dependency via Pandas)
- **Usage**: 
  - Array operations for statistical calculations
  - Mathematical functions for analysis
  - Data type handling and conversions
- **Integration**: Used implicitly through Pandas operations

#### **Gunicorn (>= 22.0)**
- **Purpose**: Production WSGI HTTP server
- **Usage**: 
  - Production deployment server
  - Process management and scaling
  - Integration with deployment platforms
- **Configuration**: Defined in `Procfile` for deployment

#### **Werkzeug (>= 2.0)**
- **Purpose**: WSGI utilities and development server
- **Usage**: 
  - HTTP exception handling
  - Development server functionality
  - Security utilities
- **Key Features**:
  - `HTTPException` for structured error handling
  - Development server for local testing
  - Security utilities for input validation

#### **Python-dateutil (>= 2.8)**
- **Purpose**: Advanced date/time parsing and manipulation
- **Usage**: 
  - Timestamp parsing from CSV files
  - Timezone handling and conversion
  - Date arithmetic for analysis
- **Critical For**: Accurate timestamp processing in trading data

## Development and Testing Dependencies

### **Statistics Module (Built-in)**
- **Purpose**: Statistical calculations for behavioral analysis
- **Usage**: 
  - Mean and standard deviation calculations
  - Population vs sample statistics
  - Coefficient of variation analysis
- **Key Functions**:
  - `statistics.mean()` for average calculations
  - `statistics.pstdev()` for population standard deviation
  - Statistical threshold calculations

### **UUID Module (Built-in)**
- **Purpose**: Unique identifier generation
- **Usage**: Trade object identification
- **Implementation**: `uuid4()` for trade IDs in Trade dataclass

### **Datetime Module (Built-in)**
- **Purpose**: Date and time handling
- **Usage**: 
  - Timestamp normalization
  - Time-based analysis (revenge trading)
  - Date filtering for goals
- **Key Classes**: `datetime`, `date`, `timezone`

### **IO Module (Built-in)**
- **Purpose**: Input/output operations
- **Usage**: File size validation and stream handling
- **Key Functions**: `io.SEEK_END` for file size checking

### **Dataclasses Module (Built-in)**
- **Purpose**: Data structure definition
- **Usage**: Trade model definition with automatic methods
- **Features**: Field defaults, factory functions, serialization

### **Typing Module (Built-in)**
- **Purpose**: Type hints and annotations
- **Usage**: 
  - Function parameter typing
  - Return type annotations
  - Generic type definitions
- **Key Types**: `Optional`, `List`, `Dict`, `Union`

## Dependency Usage Analysis

### **Data Processing Stack**
```
Raw CSV → Pandas → NumPy → Statistics → Analysis Results
```

#### **Pandas Integration**
- **File Loading**: `pd.read_csv()` with error handling
- **Data Validation**: Column existence and type checking
- **Normalization**: String cleaning and type conversion
- **Filtering**: Trade and order filtering operations

#### **Statistical Analysis**
- **Threshold Calculations**: Mean + (sigma × std_dev)
- **Outlier Detection**: Z-score methodology
- **Distribution Analysis**: Using statistics module
- **Performance Metrics**: Win rates, payoff ratios

### **Web Framework Stack**
```
HTTP Request → Flask → CORS → Business Logic → JSON Response
```

#### **Flask Integration**
- **Route Handling**: RESTful endpoint definitions
- **Request Processing**: File uploads and JSON parsing
- **Response Formatting**: JSON serialization with proper headers
- **Error Handling**: HTTP status codes and error messages

#### **CORS Configuration**
- **Multi-Origin Support**: Development and production environments
- **Security**: Restricted to specific allowed origins
- **Credentials**: Disabled for security

### **Production Deployment Stack**
```
HTTP → Gunicorn → Flask → Application Logic
```

#### **Gunicorn Configuration**
- **WSGI Server**: Production-ready HTTP server
- **Process Management**: Multi-worker support
- **Platform Integration**: Heroku, Replit compatibility

## Dependency Relationships

### **Critical Dependencies**
1. **Flask** → Core framework, application won't run without it
2. **Pandas** → Essential for data processing, no alternative
3. **Flask-CORS** → Required for frontend integration
4. **Gunicorn** → Needed for production deployment

### **Supporting Dependencies**
1. **Werkzeug** → HTTP utilities, bundled with Flask
2. **NumPy** → Numerical foundation, implicit via Pandas
3. **Python-dateutil** → Advanced datetime, could use built-in datetime

### **Built-in Dependencies**
1. **Statistics** → Could be replaced with NumPy functions
2. **UUID** → Could use alternative ID generation
3. **Datetime** → Essential for time-based analysis
4. **Dataclasses** → Could use regular classes

## Version Management

### **Minimum Versions**
- **Flask >= 3.0**: Uses modern Flask features
- **Pandas >= 2.0**: Performance improvements and API stability
- **Flask-CORS >= 4.0**: Security updates and Flask 3.0 compatibility
- **Gunicorn >= 22.0**: Python 3.10+ compatibility

### **Compatibility Considerations**
- **Python 3.10+**: Required for modern type hints and features
- **Pandas 2.0+**: Breaking changes from 1.x series
- **Flask 3.0+**: Deprecated features from 2.x series
- **NumPy**: Automatically managed by Pandas

## Security Implications

### **Direct Dependencies**
- **Flask**: Regular security updates for web vulnerabilities
- **Pandas**: Data processing security, CSV parsing safety
- **Flask-CORS**: CORS policy enforcement
- **Gunicorn**: Server security and process isolation

### **Transitive Dependencies**
- **Werkzeug**: HTTP security utilities
- **NumPy**: Numerical computation security
- **Python-dateutil**: Date parsing security
- **MarkupSafe**: Safe string handling (via Flask)

## Performance Characteristics

### **Heavy Dependencies**
1. **Pandas**: Large memory footprint, fast operations
2. **NumPy**: Efficient numerical operations
3. **Flask**: Lightweight web framework
4. **Gunicorn**: Efficient WSGI server

### **Optimization Opportunities**
- **Pandas**: Consider polars for faster CSV processing
- **NumPy**: Already optimized for numerical operations
- **Flask**: Consider FastAPI for async operations
- **Statistics**: Could use NumPy functions for better performance

## Alternative Considerations

### **Potential Replacements**
- **Pandas → Polars**: Faster CSV processing and analysis
- **Flask → FastAPI**: Better performance and auto-documentation
- **Statistics → NumPy**: Consistent numerical library usage
- **Gunicorn → Uvicorn**: ASGI server for async support

### **Migration Complexity**
- **Pandas → Polars**: Medium (API differences)
- **Flask → FastAPI**: High (different paradigm)
- **Statistics → NumPy**: Low (similar functions)
- **Gunicorn → Uvicorn**: Low (deployment configuration)

## Dependency Management Best Practices

### **Current Approach**
- **Minimal Dependencies**: Only essential libraries included
- **Version Pinning**: Minimum versions specified
- **Security Updates**: Regular dependency updates needed
- **Compatibility Testing**: Manual testing required

### **Recommendations**
1. **Add pytest**: For comprehensive testing
2. **Add black**: For code formatting consistency
3. **Add mypy**: For static type checking
4. **Add safety**: For security vulnerability scanning
5. **Add requirements-dev.txt**: Separate development dependencies

### **Deployment Considerations**
- **Container Compatibility**: All dependencies work in Docker
- **Platform Support**: Compatible with major cloud platforms
- **Installation Speed**: Relatively fast dependency installation
- **Size Optimization**: Minimal dependency footprint

---

## Mentor Dependencies

TradeHabit Mentor operates as a separate system with its own dependency stack split between frontend (Chat UI) and backend (Tool Runner).

### Mentor Frontend (Chat UI)

**Location**: `/mentor/chat-ui/`  
**Runtime**: Node.js 20+  
**Port**: 3000 (development)

#### **Production Dependencies** (from `package.json`)

##### **Next.js (14.2.5)**
- **Purpose**: React framework for Chat UI application
- **Usage**:
  - App Router for `/api/chat` endpoint
  - Server-side rendering and API routes
  - TypeScript integration
  - Development and production builds
- **Key Features Used**:
  - `app/` directory structure
  - API routes (`app/api/chat/route.ts`)
  - Server-side request handling
  - Built-in TypeScript support

##### **React (18.2.0)**
- **Purpose**: UI component library
- **Usage**:
  - Chat interface components (`Chat.tsx`, `MessageBubble.tsx`)
  - State management with hooks (`useState`)
  - Client-side rendering
- **Key Features Used**:
  - Function components
  - Hooks API (`useState`, `useEffect`)
  - Event handling

##### **React-DOM (18.2.0)**
- **Purpose**: React rendering for web
- **Usage**: DOM manipulation and rendering
- **Integration**: Automatic via Next.js

##### **OpenAI SDK (4.52.0)**
- **Purpose**: OpenAI API client library
- **Usage**:
  - Assistants API integration
  - Thread management
  - Message creation and retrieval
  - Run orchestration
- **Key Operations**:
  - `openai.beta.threads.create()`
  - `openai.beta.threads.messages.create()`
  - `openai.beta.threads.runs.create()`
  - `openai.beta.threads.runs.submitToolOutputs()`
- **Critical For**: All AI coaching functionality

#### **Development Dependencies**

##### **TypeScript (5.4.5)**
- **Purpose**: Type safety and developer experience
- **Usage**:
  - Type definitions for all components
  - Interface definitions for API responses
  - Type checking during development
- **Configuration**: `tsconfig.json`

##### **@types/node (20.11.30)**
- **Purpose**: TypeScript definitions for Node.js
- **Usage**: Type support for Node.js APIs in API routes

##### **@types/react (18.2.66)**
- **Purpose**: TypeScript definitions for React
- **Usage**: Type support for React components and hooks

##### **@types/react-dom (18.2.22)**
- **Purpose**: TypeScript definitions for React DOM
- **Usage**: Type support for React rendering APIs

#### **Environment Variables Required**
```bash
OPENAI_API_KEY=sk-...           # OpenAI API key
ASSISTANT_ID=asst_...           # OpenAI Assistant ID  
TOOL_RUNNER_BASE_URL=http://... # Tool runner endpoint
```

### Mentor Backend (Tool Runner)

**Location**: `/mentor/tool_runner/`  
**Runtime**: Python 3.9+  
**Port**: 5000 (development)

#### **Production Dependencies**

##### **Flask (latest)**
- **Purpose**: REST API server for analytics data
- **Usage**:
  - 8 endpoints serving JSON fixtures
  - Request/response handling
  - CORS support
- **Endpoints**:
  - `/get_summary_data`
  - `/get_endpoint_data`
  - `/filter_trades`
  - `/filter_losses`
  - Health check and utilities

##### **Flask-CORS (latest)**
- **Purpose**: Cross-origin resource sharing
- **Usage**: Enable Chat UI (port 3000) to call Tool Runner (port 5000)
- **Configuration**: `CORS(app, resources={r"/*": {"origins": "*"}})`
- **Note**: Currently allows all origins (development only)

#### **Built-in Python Modules**
- **json**: JSON fixture loading and parsing
- **os**: File system operations for fixture discovery
- **statistics**: Loss statistics calculations (mean, std dev)
- **datetime**: Timestamp parsing and filtering
- **typing**: Type hints for function signatures

### Mentor Prompt Corpus

**Location**: `/mentor/prompts/`  
**Format**: 13 markdown and JSON files  
**Dependencies**: None (static text files loaded by OpenAI)

#### **Prompt Files** (13 files)
- `assistant/system_instructions/system_instructions.md` (1)
- `persona/*.md` (3 files)
- `knowledge_base/*.md` (4 files)
- `templates/*.{md,json}` (3 files)
- `conversation_starters/*.md` (2 files)

#### **Function Schemas** (4 files)
- `assistant/functions/get_summary_data.json`
- `assistant/functions/get_endpoint_data.json`
- `assistant/functions/filter_trades.json`
- `assistant/functions/filter_losses.json`

**Purpose**: Define OpenAI Assistant function calling interface

### Mentor Dependency Relationships

#### **Frontend Stack**
```
Next.js → React → OpenAI SDK → Tool Runner
```

#### **Backend Stack**
```
Flask → JSON Fixtures (9 files totaling ~181KB)
```

#### **AI Stack**
```
Chat UI → OpenAI Assistants API → Prompt Corpus (13 files)
```

### Mentor Version Management

#### **Critical Versions**
- **Next.js 14.2.5**: Stable App Router with API routes
- **React 18.2.0**: Concurrent rendering features
- **OpenAI SDK 4.52.0**: Assistants API support (beta)
- **TypeScript 5.4.5**: Modern TypeScript features

#### **Compatibility Notes**
- **Node.js 20+**: Required for Next.js 14
- **Python 3.9+**: Required for type hints in tool runner
- **OpenAI Assistants API**: Beta API, subject to changes

### Mentor Security Implications

#### **External Service Dependencies**
- **OpenAI API**: Third-party AI provider
  - API key security critical
  - Data sent to OpenAI servers
  - Rate limiting and cost considerations
  - Beta API stability risks

#### **Authentication**
- ⚠️ **No authentication currently implemented**
- Tool Runner: CORS open to all origins (dev only)
- Chat UI: No user authentication
- OpenAI API key stored in environment variables

#### **Data Privacy**
- User data sent to OpenAI API
- Thread persistence on OpenAI servers
- No local conversation storage
- Synthetic test data only (currently)

### Mentor Performance Characteristics

#### **Bundle Sizes**
- Next.js build: ~200KB gzipped (estimated)
- OpenAI SDK: ~50KB (when bundled)
- Total frontend bundle: <500KB

#### **API Latency**
- Tool Runner (cached): <100ms
- Tool Runner (first request): ~50-200ms (disk I/O)
- OpenAI API call: 1-5s (depends on response complexity)
- End-to-end conversation turn: 2-6s

#### **Data Sizes**
- JSON Fixtures: 181KB total (9 files)
  - trades.json: 131KB (largest)
  - losses.json: 45KB
  - insights.json: 2.8KB
  - Others: <1KB each

### Mentor Alternative Considerations

#### **Potential Replacements**
- **OpenAI SDK → Anthropic/Claude**: Different AI provider
- **Next.js → Vite + React**: Lighter build tooling
- **Flask → FastAPI**: Async support for tool runner
- **OpenAI Assistants → Custom orchestration**: More control, more complexity

#### **Migration Complexity**
- **OpenAI → Other AI**: High (function calling differences)
- **Next.js → Vite**: Medium (routing differences)
- **Flask → FastAPI**: Low (similar APIs)
- **Assistants → Custom**: Very High (reimplementing thread management)

### Mentor Deployment Considerations

#### **Current State**
- ⚠️ **Development Only**: Not production-ready
- **Separate Services**: Chat UI and Tool Runner run independently
- **No Integration**: Not connected to main backend
- **Manual Setup**: Requires environment configuration

#### **Production Requirements**
1. **Unified Backend**: Integrate tool runner into main API
2. **Authentication**: Add user authentication and API security
3. **Database**: Replace JSON fixtures with database queries
4. **Monitoring**: Add logging, tracing, and error tracking
5. **Rate Limiting**: Protect OpenAI API usage and costs
6. **CDN**: Optimize Next.js static assets delivery

### Mentor Dependency Management

#### **Current Approach**
- **Frontend**: npm with `package-lock.json` for reproducible builds
- **Backend**: Python with no `requirements.txt` (uses core Python only)
- **Versions**: Exact versions pinned in package.json

#### **Recommendations**
1. **Add `requirements.txt`**: Document Python dependencies for tool runner
2. **Security Scanning**: Add `npm audit` to CI/CD
3. **Dependency Updates**: Monitor OpenAI SDK for API changes
4. **Development Dependencies**: Separate dev and production dependencies

---

This dependency analysis provides a comprehensive overview of both the core backend and Mentor system dependencies, their purposes, and their relationships within the TradeHabit architecture.