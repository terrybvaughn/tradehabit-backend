# State Management

## Overview

This document covers state management for both TradeHabit systems:
- **Core Analytics Backend** (documented below) - Simple in-memory state for session-based analysis
- **TradeHabit Mentor** (see [Mentor State Management](#mentor-state-management)) - Separate prototype with external thread storage

---

## Core Analytics Backend

TradeHabit's core backend employs a **simple in-memory state management pattern** suitable for single-session behavioral analysis. The backend maintains stateful data structures during the user's session, while the frontend (React) uses modern state management libraries for UI state.

## Backend State Management

### Global State Structure

The Flask application maintains global state through module-level variables in `app.py`:

```python
# Primary data structures
trade_objs = []        # List[Trade] - Analyzed trade objects
order_df = None        # pd.DataFrame - Original order data

# Configuration state
THRESHOLDS = {
    "k": 1.0,              # Revenge-trade window multiplier
    "sigma_loss": 1.0,     # Outsized loss sigma multiplier
    "sigma_risk": 1.5,     # Excessive risk sigma multiplier
    "vr": 0.35,            # Risk sizing variation threshold
}
```

### State Lifecycle

#### 1. **Session Initialization**
```python
# State begins empty
trade_objs = []
order_df = None
```

#### 2. **Data Upload** (`POST /api/analyze`)
```python
def analyze():
    global trade_objs, order_df
    
    # Load and validate CSV data
    order_df = load_orders(f)
    
    # Transform orders into trades
    trades, _ = count_trades(order_df)
    
    # Update global state
    trade_objs.clear()
    trade_objs.extend(trades)
    
    # Perform analysis (modifies trade_objs in-place)
    analyze_all_mistakes(trade_objs, order_df, sigma, k, sigma_risk)
```

#### 3. **State Persistence During Session**
- **Read Operations**: All GET endpoints access `trade_objs` and `order_df`
- **Configuration Updates**: `POST /api/settings` modifies `THRESHOLDS`
- **Re-analysis**: Settings changes trigger re-analysis of existing data

#### 4. **Session Termination**
- **No Persistence**: State lost when server restarts
- **Memory Cleanup**: Automatic garbage collection when session ends

### State Mutation Patterns

#### **In-Place Mutation**
The analytics modules follow a mutation-based approach:

```python
def analyze_all_mistakes(trades, order_df, sigma, k, sigma_risk):
    """Modifies trade objects in-place by adding mistakes to mistakes list"""
    
    # Each analyzer mutates the same Trade objects
    analyze_trades_for_no_stop_mistake(trades, order_df)
    analyze_trades_for_excessive_risk(trades, sigma_risk)
    analyze_trades_for_outsized_loss(trades, sigma)
    analyze_trades_for_revenge(trades, k)
    analyze_trades_for_risk_sizing_consistency(trades)
```

#### **Mistake Accumulation**
Each analyzer adds mistakes to the `Trade.mistakes` list:

```python
# From Trade dataclass
mistakes: List[str] = field(default_factory=list)

# Example mutation
if trade_needs_stop_loss:
    trade.mistakes.append("no stop-loss order")
```

#### **Threshold-Based Re-analysis**
When thresholds change, existing data is re-analyzed:

```python
def settings():
    global trade_objs, order_df, THRESHOLDS
    
    # Update thresholds
    THRESHOLDS[key] = float(val)
    
    # Re-analyze existing data
    if trade_objs and order_df is not None:
        # Clear old mistakes
        for t in trade_objs:
            t.mistakes.clear()
        
        # Re-run analysis with new thresholds
        analyze_all_mistakes(trade_objs, order_df, ...)
```

### State Access Patterns

#### **Centralized Access**
All endpoints access the same global state:

```python
@app.get("/api/summary")
def get_summary():
    global trade_objs
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")
    # Process trade_objs...

@app.get("/api/trades")
def get_trades():
    global trade_objs
    # Access same state...
```

#### **State Validation**
Endpoints validate state before processing:

```python
def check_state():
    if not trade_objs:
        abort(400, "No trades have been analyzed yet")
    if 'order_df' not in globals() or order_df is None:
        abort(400, "Order data is missing")
```

## Frontend State Management (External)

### Technology Stack
- **Zustand**: Global state management
- **TanStack Query**: Server state management and caching
- **React State**: Local component state

### State Architecture

#### **Global State (Zustand)**
```typescript
interface AppState {
  trades: Trade[]
  summary: SummaryData
  settings: AnalysisSettings
  insights: InsightsData
}
```

#### **Server State (TanStack Query)**
```typescript
// Cached API responses
const { data: trades } = useQuery(['trades'], fetchTrades)
const { data: summary } = useQuery(['summary'], fetchSummary)
const { data: insights } = useQuery(['insights'], fetchInsights)
```

#### **Local State (React)**
```typescript
// Component-specific state
const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null)
const [filterOptions, setFilterOptions] = useState<FilterState>({})
```

### Data Flow Patterns

#### **Server-to-Client Synchronization**
1. **File Upload**: Client uploads CSV → Server processes → Client receives analysis
2. **Settings Update**: Client updates settings → Server re-analyzes → Client refreshes data
3. **Real-time Updates**: Client polls endpoints for updated analysis

#### **Client-Side Caching**
- **TanStack Query**: Caches server responses with automatic invalidation
- **Optimistic Updates**: UI updates immediately for settings changes
- **Background Refresh**: Automatic re-fetching on window focus

## Data Consistency Patterns

### Backend Consistency

#### **Atomic Operations**
State changes are atomic within request handlers:

```python
def analyze():
    # Atomic state update
    trade_objs.clear()
    trade_objs.extend(new_trades)
    
    # Analysis is completed before response
    analyze_all_mistakes(trade_objs, ...)
    return jsonify(response)
```

#### **Mutation Ordering**
Analysis steps follow a specific order to ensure consistency:

1. **Clear existing mistakes** (on re-analysis)
2. **Stop-loss analysis** (highest priority)
3. **Risk-based analysis** (depends on risk calculations)
4. **Time-based analysis** (depends on trade sequencing)
5. **Insight generation** (depends on all mistake flags)

### Frontend Consistency

#### **Query Invalidation**
```typescript
// After settings update
queryClient.invalidateQueries(['summary'])
queryClient.invalidateQueries(['insights'])
queryClient.invalidateQueries(['goals'])
```

#### **Optimistic Updates**
```typescript
// Update settings immediately
settingsStore.updateSettings(newSettings)

// Then sync with server
await updateSettingsAPI(newSettings)
```

## State Persistence

### Backend Persistence
- **No Database**: All state in memory
- **Session-Based**: State lost on server restart
- **File-Based**: Data loaded from CSV uploads

### Frontend Persistence
- **Browser Storage**: Settings and preferences
- **Session Storage**: Temporary UI state
- **No Long-term Storage**: Data re-fetched from server

## Performance Considerations

### Memory Management

#### **Backend**
- **Linear Growth**: Memory usage scales with trade count
- **Efficient Structures**: Pandas DataFrames for bulk operations
- **Garbage Collection**: Automatic cleanup on session end

#### **Frontend**
- **Query Caching**: Reduces server requests
- **Selective Updates**: Only re-fetch changed data
- **Virtual Scrolling**: For large trade lists

### Optimization Strategies

#### **Backend**
```python
# Efficient iteration
for trade in trade_objs:
    # In-place mutation avoids object copying
    trade.mistakes.append(mistake_type)

# Batch operations
df_operations = order_df.groupby('symbol').agg({...})
```

#### **Frontend**
```typescript
// Memoized computations
const expensiveCalculation = useMemo(() => {
  return computeIntensiveOperation(trades)
}, [trades])

// Debounced updates
const debouncedUpdate = useDebouncedCallback(
  updateSettings, 300
)
```

## Error Handling in State Management

### Backend Error Recovery
```python
try:
    order_df = load_orders(f)
    trades, _ = count_trades(order_df)
    trade_objs.clear()
    trade_objs.extend(trades)
except Exception as e:
    # State remains unchanged on error
    return error_response(500, str(e))
```

### Frontend Error Boundaries
```typescript
// Query error handling
const { data, error, isLoading } = useQuery(
  ['trades'],
  fetchTrades,
  {
    retry: 3,
    onError: (error) => {
      // Fallback to cached data
      showErrorNotification(error.message)
    }
  }
)
```

## State Management Best Practices

### Backend
1. **Validate State**: Always check if data exists before processing
2. **Atomic Updates**: Complete operations before returning responses
3. **Clear Error Messages**: Provide specific state-related error information
4. **Consistent Mutation**: Follow the same pattern across all analyzers

### Frontend
1. **Separate Concerns**: Use different state solutions for different needs
2. **Cache Strategically**: Balance performance with data freshness
3. **Handle Loading States**: Provide feedback during state transitions
4. **Error Boundaries**: Graceful degradation when state operations fail

---

## Mentor State Management

**Status**: Development prototype with temporary state patterns. Will be redesigned with user accounts and persistence.

### Current State Architecture

#### **Conversation State (External)**
- **Storage**: OpenAI thread storage (external to application)
- **Lifecycle**: Threads persist across sessions on OpenAI servers
- **Access**: Via OpenAI Assistants API using thread IDs
- **Limitation**: No local thread management or user ownership

#### **Tool Runner State (In-Memory)**
- **Cache**: In-memory dictionary of loaded JSON fixtures
- **Lifecycle**: Cache persists until tool runner restart
- **Pattern**: Similar to core backend - no persistence
```python
CACHE: dict[str, Any] = {}  # In-memory fixture cache
```

#### **Chat UI State (React)**
- **Local State**: Message history managed with `useState`
- **Thread Tracking**: Thread ID stored in component state
- **No Persistence**: Conversation lost on page refresh
```typescript
const [messages, setMessages] = useState<Msg[]>([])
const [threadId, setThreadId] = useState<string | undefined>()
```

### Key Differences from Core Backend

| Aspect | Core Backend | Mentor |
|--------|--------------|--------|
| **Conversation State** | N/A | Stored on OpenAI servers |
| **Data State** | In-memory global | In-memory cache + JSON fixtures |
| **Persistence** | None | Threads persist on OpenAI only |
| **Multi-user** | Single session | No isolation (shared fixtures) |

### Future State Management (Planned)

When user accounts are added:
- **User-specific data**: Replace shared fixtures with per-user database queries
- **Thread ownership**: Associate OpenAI threads with user accounts
- **Conversation history**: Store thread metadata locally for user management
- **Settings persistence**: Store per-user Mentor preferences
- **Unified state**: Integrate Mentor state with core backend state model

For complete Mentor architecture details, see [`docs/mentor.md`](./mentor.md).

---

This state management approach provides a simple, effective solution for the application's behavioral analysis needs while maintaining good performance and user experience.