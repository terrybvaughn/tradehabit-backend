# TradeHabit Mentor – Technical Documentation

## Overview

**TradeHabit Mentor** is an AI-powered trading coach that turns trade data into an always-on mentor that pinpoints bad habits, explains analytics, sets realistic goals, and provides accountability. Modeled after an experienced trader who delivers hard truths gently, Mentor provides candid, supportive, and personalized guidance to help traders:

1. **Understand analytics** – Explanations of TradeHabit metrics, diagnostics, and detection methods
2. **Gain deeper insights** – Clear understanding of behavioral patterns affecting performance
3. **Prioritize improvements** – Identify which behaviors need attention most
4. **Set achievable goals** – Assistance with realistic, attainable goal-setting
5. **Stay accountable** – Motivational support and progress monitoring against goals

Mentor provides the frank, one-to-one guidance of a seasoned trading coach without the high costs or difficulty of finding a qualified mentor.

### Technical Implementation

Mentor uses OpenAI's Assistants API with function calling to fetch analytics data from TradeHabit's API endpoints (currently served from local JSON fixtures) and deliver structured, educational responses based on a comprehensive prompt corpus.

**Current Status**: Stable for development and testing with local JSON fixtures. Not yet production-hardened.

---

## Architecture

### System Components

```
User
  ↓
Chat UI (Next.js 14 + React)
  ↓ /api/chat
Assistant Orchestrator (OpenAI Assistants API)
  ↓ Function Calls
Tool Runner (Flask + Python)
  ↓ File I/O
JSON Fixtures (Static Data)
```

### Component Details

#### **Chat UI** (`/mentor/chat-ui/`)
- **Framework**: Next.js 14.2.5, React 18.2.0, TypeScript 5.4.5
- **Port**: 3000 (development)
- **Key Files**:
  - `src/components/Chat.tsx` – Main chat interface
  - `src/lib/runAssistant.ts` – Assistant orchestration logic with retry handling
  - `src/app/api/chat/route.ts` – Next.js API route handler
  - `src/lib/openai.ts` – OpenAI client configuration
- **Environment Variables**:
  - `OPENAI_API_KEY` – OpenAI API key
  - `ASSISTANT_ID` – OpenAI Assistant ID
  - `TOOL_RUNNER_BASE_URL` – URL to tool runner (e.g., `http://localhost:5000`)

#### **Tool Runner** (`/mentor/tool_runner/`)
- **Framework**: Flask with CORS enabled
- **Port**: 5000 (development)
- **Purpose**: Serves analytics data from JSON fixtures via REST endpoints
- **Key Features**:
  - In-memory caching of JSON fixtures
  - Pagination and filtering support
  - Automatic endpoint discovery from available JSON files
  - Canonicalization of endpoint names (hyphens/underscores/spaces treated as equivalent)
- **Data Location**: `mentor/tool_runner/static/` (9 JSON fixtures)

#### **Prompt Corpus** (`/mentor/prompts/`)
- **System Instructions**: Core persona, conversation guidelines, routing logic
- **Knowledge Base**: Analytics explanations, metric mappings, TradeHabit functionality
- **Templates**: Response formats, explanation patterns
- **Function Schemas**: Tool definitions for OpenAI Assistant (`/assistant/functions/`)

---

## Data Flow

### Typical Conversation Flow

1. **User Input**: User sends message via Chat UI
2. **Thread Management**: Frontend creates/reuses OpenAI thread
3. **Message Creation**: User message added to thread
4. **Run Creation**: OpenAI Assistant run initiated
5. **Function Calling**: Assistant requests data via function calls
   - `get_summary_data` – Portfolio-level metrics
   - `get_endpoint_data` – Category-specific analytics
   - `filter_trades` – Filtered/paginated trade list
   - `filter_losses` – Filtered/paginated loss records with statistics
6. **Tool Execution**: Frontend calls Tool Runner endpoints
7. **Tool Response**: Tool Runner returns JSON data
8. **Run Continuation**: Function outputs submitted to OpenAI
9. **Assistant Response**: AI generates structured response using prompt corpus
10. **UI Render**: Chat UI displays assistant message

### Tool Runner Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check (service name) |
| `/health` | GET | Health check (status: OK) |
| `/list_endpoints` | GET | List available fixture keys |
| `/refresh_cache` | POST | Clear in-memory cache |
| `/get_summary_data` | POST | Fetch summary.json (portfolio totals) |
| `/get_endpoint_data` | POST | Fetch any analytics fixture (keys-only, full, or paginated) |
| `/filter_trades` | POST | Filter/sort/paginate trades.json |
| `/filter_losses` | POST | Filter/sort/paginate losses.json with loss statistics |

---

## Function Tools

The OpenAI Assistant has 4 function tools defined. Function schemas are located in `mentor/prompts/assistant/functions/`:

| Schema File | Function Name |
|-------------|---------------|
| `get_summary_data.json` | `get_summary_data` |
| `get_endpoint_data.json` | `get_endpoint_data` |
| `filter_trades.json` | `filter_trades` |
| `filter_losses.json` | `filter_losses` |

### 1. `get_summary_data`
- **Purpose**: Fetch portfolio-level summary metrics
- **Parameters**: None
- **Returns**: Overall trading statistics (wins/losses, mistake counts, etc.)
- **Use Cases**: Session initialization, high-level overviews

### 2. `get_endpoint_data`
- **Purpose**: Fetch category-specific analytics (insights, revenge, excessive-risk, risk-sizing, winrate-payoff, stop-loss)
- **Parameters**:
  - `name` (required): Endpoint name from allowed enum
  - `keys_only` (optional): Return only top-level keys and array lengths
  - `top` (optional): Page through a specific top-level array
  - `fields` (optional): Project specific fields in results
  - `include_total` (optional): Include total count when paginating
  - `offset`, `max_results` (optional): Pagination controls
- **Returns**: Full fixture data or metadata depending on parameters
- **Use Cases**: Fetching methodology details, aggregated analytics

### 3. `filter_trades`
- **Purpose**: Query trades with complex filtering, sorting, pagination
- **Parameters**: Filters (mistakes, time ranges, side, symbol, PnL ranges, etc.), sorting, pagination
- **Returns**: Paginated list of trades matching filters with `total`, `returned`, `has_more`
- **Use Cases**: "Show me trades with X mistake", "How many trades in February?"

### 4. `filter_losses`
- **Purpose**: Query losing trades with outsized loss analysis
- **Parameters**: Similar filters to `filter_trades`, plus `extrema` for min/max queries
- **Returns**: Paginated loss records plus `loss_statistics` (mean, std dev, threshold, counts)
- **Use Cases**: "What's my worst loss?", Loss Consistency Chart analysis

---

## Prompt Architecture

### Prompt Loading Order
(See `prompts/prompt_loading_order.md`)

1. **Foundation**: Core persona, conversation guidelines, trading expertise
2. **Authoritative Knowledge**: Metric mappings (single source of truth), TradeHabit functionality, analytics explanations
3. **Application Frameworks**: Routing table (intent classification), explanation patterns, response formats

### Prompt Files Reference

All prompt files are located in `mentor/prompts/`:

#### System Instructions
| File | Purpose |
|------|---------|
| `assistant/system_instructions/system_instructions.md` | Master routing logic, tool policies, response construction rules |

#### Persona
| File | Purpose |
|------|---------|
| `persona/core_persona.md` | Mentor's personality, boundaries, coaching philosophy |
| `persona/conversation_guidelines.md` | Interaction patterns, conversation flow rules |
| `persona/trading_expert.md` | Trading domain expertise and knowledge scope |

#### Knowledge Base 
| File | Purpose |
|------|---------|
| `knowledge_base/metric_mappings.md` | Canonical terminology and definitions (single source of truth) |
| `knowledge_base/analytics_explanations.md` | Formulas, thresholds, detection algorithms |
| `knowledge_base/tradehabit_functionality.md` | Complete feature and capability documentation |
| `knowledge_base/trading_concepts.md` | General trading concepts and terminology |

#### Templates
| File | Purpose |
|------|---------|
| `templates/routing_table.json` | Intent classification and tool selection rules |
| `templates/explanation_patterns.md` | Content templates for different question types |
| `templates/response_formats.md` | Structural templates for responses |

#### Conversation Starters
| File | Purpose |
|------|---------|
| `conversation_starters/first_time_user.md` | Greeting and onboarding narratives for new users |
| `conversation_starters/returning_user.md` | Re-engagement narratives for returning users |

---

## Development Setup

### Prerequisites
- Python 3.9+ (for tool runner)
- Node.js 20+ (for chat UI)
- OpenAI API key with Assistants API access
- OpenAI Assistant configured with function tools

### Backend (Tool Runner)
```bash
cd mentor/tool_runner
python tool_runner.py  # Runs on port 5000
```

### Frontend (Chat UI)
```bash
cd mentor/chat-ui
npm install
# Set environment variables in .env.local:
# OPENAI_API_KEY=sk-...
# ASSISTANT_ID=asst_...
# TOOL_RUNNER_BASE_URL=http://localhost:5000
npm run dev  # Runs on port 3000
```

### JSON Fixtures
Place test data in `mentor/tool_runner/static/`:
- `summary.json` – Portfolio summary
- `trades.json` – All trades
- `losses.json` – Losing trades
- `insights.json` – Behavioral insights
- `revenge.json` – Revenge trading analysis
- `excessive-risk.json` – Excessive risk analysis
- `risk-sizing.json` – Risk sizing consistency
- `stop-loss.json` – Stop-loss compliance
- `winrate-payoff.json` – Win rate and risk-reward analysis

---

## Known Limitations & Gotchas

### Performance
- **Large fixtures**: Timeouts possible with fixtures >1MB; use pagination
- **Caching**: First request to each fixture loads from disk; subsequent requests served from memory
- **Rate limiting**: OpenAI API rate limits apply; frontend includes retry logic for 429 errors

### Data
- **Static fixtures**: Tool runner serves pre-generated JSON; no live data integration
- **Hard pagination cap**: Maximum 50 items per request to protect token limits

### Security
- **No authentication**: Tool runner has CORS enabled for all origins (development only)
- **No multi-tenancy**: All requests share same fixture data
- **Environment secrets**: API keys and Assistant ID stored in environment variables

### Integration
- **No backend API**: Chat UI directly calls OpenAI and Tool Runner; no unified TradeHabit backend API yet
- **Thread persistence**: Threads stored in OpenAI; no local thread management

---

## Future Considerations

### Production Readiness
- [ ] Authentication/authorization for tool runner
- [ ] Rate limiting and request throttling
- [ ] Observability (logging, tracing, metrics)
- [ ] Error handling and graceful degradation
- [ ] Database integration (replace JSON fixtures)
- [ ] Multi-tenant data isolation

### Feature Enhancements
- [ ] Thread management and history
- [ ] User preferences and parameter tuning
- [ ] Export conversation transcripts
- [ ] Streaming responses for better UX
- [ ] Assistant performance monitoring

---

## Related Documentation
- `docs/api.md` – Main TradeHabit API documentation
- `docs/architecture.md` – Overall system architecture
- `mentor/prompts/prompt_loading_order.md` – Prompt corpus organization
