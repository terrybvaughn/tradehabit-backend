# TradeHabit Mentor Chat UI

A Next.js chat interface for the TradeHabit Mentor AI assistant, featuring optimized tool calling and real-time behavioral analytics coaching.

## Prerequisites
- **Node.js 18+**
- **Tool Runner**: Running on port 5000 and exposed via ngrok
- **OpenAI API Key**: For Assistant API access
- **TradeHabit Data**: Static JSON snapshots in tool runner

## Quick Start

1. **Start the tool runner**:
   ```bash
   cd mentor/tool_runner
   python tool_runner.py
   ```

2. **Expose with ngrok**:
   ```bash
   ngrok http 5000
   ```

3. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your values
   ```

4. **Install and run**:
   ```bash
   npm install
   npm run dev
   ```

5. **Visit**: http://localhost:3000

## Environment Configuration

Create `.env.local` with:
```env
OPENAI_API_KEY=your_openai_api_key
TOOL_RUNNER_BASE_URL=https://your-ngrok-url.ngrok-free.app
ASSISTANT_ID=your_assistant_id
```

## How It Works

### Architecture
- **Frontend**: React chat interface at `http://localhost:3000`
- **Backend**: Next.js API routes handle Assistant communication
- **Tool Runner**: Flask service with optimized caching and smart routing
- **Data Flow**: User message → Assistant API → Tool calls → Tool Runner → Response

### Enhanced Tool Calling
- **In-memory caching**: Reduces response times for repeated requests
- **Smart API routing**: Automatic delegation to specialized filter endpoints
- **Payload optimization**: Prevents large array returns, uses pagination
- **Field projection**: Returns only requested fields to reduce token usage

## Available Tools

### Core Analytics
- **`get_summary_data`**: Trading performance summary (win rate, mistake counts, streaks)
- **`get_endpoint_data`**: Generic endpoint data with smart routing and pagination
- **`filter_trades`**: Advanced trade filtering with time ranges, mistake types, sorting
- **`filter_losses`**: Loss analysis with pagination, sorting, and field projection
- **`refresh_cache`**: Cache management for data updates

### Smart Routing
- `get_endpoint_data` with `top="trades"` → automatically routes to `filter_trades()`
- `get_endpoint_data` with `top="losses"` → automatically routes to `filter_losses()`
- Prevents Mentor from repeatedly requesting full datasets

## Performance Features

### Caching
- **Automatic**: JSON files cached in memory after first load
- **Invalidation**: Use `refresh_cache` endpoint when data updates
- **Benefits**: Eliminates repeated file reads, faster response times

### Optimization
- **Pagination**: Built-in support for `max_results`, `offset`, `fields`
- **Filtering**: Time ranges, mistake types, numeric ranges, sorting
- **Field projection**: Return only specific fields to reduce payload size
- **Metadata queries**: Use `keys_only=true` for structure exploration

## Troubleshooting

### Common Issues
- **Tool call failures**: Verify ngrok URL and tool runner status
- **Large responses**: Use pagination parameters (`max_results`, `fields`)
- **Stale data**: Call `refresh_cache` endpoint when JSON files update
- **Memory usage**: Restart tool runner if cache grows too large

### Performance Tips
- Use `keys_only=true` for structure exploration
- Leverage `top` parameter for automatic pagination
- Apply field projection to reduce token usage
- Cache invalidation only when data actually changes

## Development Notes

- **Polling**: Current implementation uses polling for reliability
- **Security**: Keep `OPENAI_API_KEY` server-side only
- **Streaming**: Can be added later for real-time responses
- **Error Handling**: Graceful degradation when tools are unavailable

## Mentor Capabilities

The Mentor provides:
- **Behavioral analytics**: Identifies trading mistakes and patterns
- **Parameter calibration**: Helps optimize detection thresholds
- **Goal setting**: Tracks progress on behavioral improvements
- **Data-driven insights**: All responses grounded in actual trading data
- **Authoritative scope**: Prevents hallucination and feature invention