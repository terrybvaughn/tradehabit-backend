# Data Requirements

## Overview

TradeHabit processes NinjaTrader CSV exports to perform behavioral trading analysis. The application has specific data format requirements, validation rules, and processing limitations that must be understood for successful implementation.

## Input Data Format

### **Required CSV Structure**

#### **NinjaTrader Export Format**
The application expects CSV files exported from NinjaTrader with the following columns:

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `Timestamp` | DateTime | Order timestamp | `2024-01-15 14:30:00` |
| `Fill Time` | DateTime | Order fill timestamp | `2024-01-15 14:30:15` |
| `B/S` | String | Buy/Sell indicator | `"B"` or `"S"` |
| `Contract` | String | Trading instrument symbol | `"MNQH5"` |
| `filledQty` | Integer | Filled quantity | `2` |
| `Avg Fill Price` | Float | Average fill price | `16245.50` |
| `Order ID` | Integer | Unique order identifier | `12345` |
| `Status` | String | Order status | `"Filled"` |

#### **Column Mapping**
The system internally renames columns for consistency:

```python
COLUMN_MAPPING = {
    "B/S": "side",
    "Contract": "symbol", 
    "filledQty": "qty",
    "Avg Fill Price": "price",
    "Order ID": "order_id_original",
    "Timestamp": "ts",
    "Fill Time": "fill_ts"
}
```

### **Data Validation Rules**

#### **Required Fields**
All CSV files must contain these exact column headers:
- `Timestamp`
- `Fill Time`
- `B/S`
- `Contract`
- `filledQty`
- `Avg Fill Price`
- `Order ID`
- `Status`

#### **Data Type Validation**
- **Timestamps**: Must be parseable as datetime objects
- **Quantities**: Must be positive integers
- **Prices**: Must be positive floats
- **Side**: Must be "B" (Buy) or "S" (Sell)
- **Status**: Must be "Filled" (other statuses filtered out)

#### **Data Quality Checks**
```python
# Order filtering criteria
valid_orders = df[
    (df['Status'] == 'Filled') &
    (df['qty'] > 0) &
    (df['fill_ts'].notna()) &
    (df['ts'].notna())
]
```

## File Requirements

### **File Format Constraints**
- **Extension**: Must be `.csv` (case-insensitive)
- **Size Limit**: Maximum 2MB per file
- **Encoding**: UTF-8 recommended
- **Delimiter**: Comma-separated values

### **File Validation Process**
```python
def validate_upload(file_storage):
    # Extension check
    if not file_storage.filename.lower().endswith('.csv'):
        raise ValueError("CSV format required")
    
    # Size check
    file_storage.seek(0, io.SEEK_END)
    if file_storage.tell() > 2 * 1024 * 1024:  # 2MB
        raise ValueError("File too large")
    
    file_storage.seek(0)
    return True
```

## Data Processing Pipeline

### **Stage 1: Initial Loading**
```python
def load_orders(file_storage) -> pd.DataFrame:
    # Read CSV with pandas
    df = pd.read_csv(file_storage)
    
    # Normalize string fields
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    
    return df
```

### **Stage 2: Column Validation**
```python
def validate_columns(df):
    required_columns = {
        'ts', 'fill_ts', 'qty', 'Status', 
        'side', 'symbol', 'price'
    }
    
    missing = required_columns - set(df.columns)
    if missing:
        raise KeyError(f"Missing columns: {missing}")
```

### **Stage 3: Data Normalization**
```python
def normalize_and_prepare_orders_df(df):
    # Rename columns to internal format
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Convert timestamps to UTC
    df = normalize_timestamps_in_df(df)
    
    # Filter valid orders
    df = df[df['Status'] == 'Filled']
    
    return df
```

### **Stage 4: Trade Construction**
```python
def count_trades(order_df):
    # Group orders by symbol and time
    # Track positions and detect trade completions
    # Return list of Trade objects
```

## Data Flows

### **Order-to-Trade Transformation**

#### **Position Tracking Algorithm**
```python
positions = {}  # {symbol: PositionInfo}

for order in orders:
    symbol = order['symbol']
    
    if symbol not in positions:
        # New position
        positions[symbol] = create_position(order)
    else:
        # Existing position
        if same_direction(order, positions[symbol]):
            # Scale-in: add to position
            update_position(positions[symbol], order)
        else:
            # Exit: create trade and update position
            trade = create_trade(positions[symbol], order)
            trades.append(trade)
            update_or_close_position(positions[symbol], order)
```

#### **Trade Object Construction**
```python
@dataclass
class Trade:
    id: str = field(default_factory=lambda: str(uuid4()))
    symbol: str = ""
    entry_time: datetime = None
    entry_price: float = 0.0
    entry_qty: int = 0
    exit_time: datetime = None
    exit_price: float = 0.0
    exit_qty: int = 0
    side: str = ""
    exit_order_id: Optional[int] = None
    pnl: Optional[float] = None
    mistakes: List[str] = field(default_factory=list)
    risk_points: Optional[float] = None
```

## Timezone Handling

### **Timestamp Normalization**
```python
def normalize_timestamps_in_df(df):
    # Assume America/New_York if timezone-naive
    ny_tz = pytz.timezone('America/New_York')
    
    for col in ['ts', 'fill_ts']:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Localize to NY timezone, then convert to UTC
        df[col] = df[col].dt.tz_localize(ny_tz, ambiguous='infer')
        df[col] = df[col].dt.tz_convert(pytz.UTC)
```

### **Time-Based Analysis Requirements**
- **Revenge Trading**: Requires accurate entry time sequencing
- **Stop-Loss Detection**: Needs precise order timing (60-second windows)
- **Hold Time Calculations**: Depends on entry/exit timestamp accuracy

## Statistical Data Requirements

### **Minimum Data Thresholds**
- **Minimum Trades**: 1 (no minimum enforced)
- **Loss Analysis**: Requires at least 2 losing trades for standard deviation
- **Risk Analysis**: Needs trades with stop-loss orders
- **Revenge Analysis**: Requires sequence of trades with losses

### **Data Distribution Requirements**
```python
# Outsized loss analysis
losses = [t.points_lost for t in trades if t.pnl < 0]
if len(losses) > 1:
    mean_loss = statistics.mean(losses)
    std_loss = statistics.pstdev(losses)
    threshold = mean_loss + (sigma * std_loss)
```

### **Statistical Validation**
- **Standard Deviation**: Uses population standard deviation (`pstdev`)
- **Outlier Detection**: Requires sufficient data points for meaningful analysis
- **Coefficient of Variation**: Needs consistent risk data across trades

## Data Limitations

### **Current Constraints**
- **Single Session**: No data persistence between sessions
- **Memory Storage**: All data held in memory during processing
- **File Size**: 2MB limit on uploaded files
- **Single File**: No multi-file processing support

### **Processing Limitations**
- **Partial Fills**: Handled but may affect accuracy
- **Complex Orders**: OCO orders supported, advanced order types may not be
- **Multi-Symbol**: Supported but analyzed separately
- **Intraday Only**: No multi-day position tracking

### **Analysis Limitations**
- **Historical Context**: No long-term trend analysis
- **Market Data**: No market context (volatility, news, etc.)
- **Account Info**: No account size or risk percentage calculations
- **Commission**: Not included in PnL calculations

## Error Handling

### **File Processing Errors**
```python
try:
    order_df = load_orders(file)
except pd.errors.ParserError:
    return error_response(400, "CSV format not recognized")
except KeyError as e:
    return error_response(400, f"Missing columns: {e}")
except Exception as e:
    return error_response(500, f"Processing error: {e}")
```

### **Data Quality Issues**
- **Missing Timestamps**: Filtered out with warning
- **Invalid Quantities**: Filtered out with warning
- **Malformed Prices**: Filtered out with warning
- **Unknown Symbols**: Processed but noted

### **Graceful Degradation**
- **Partial Data**: Analysis continues with available data
- **Missing Stop Orders**: Stop-loss analysis reports limitations
- **Insufficient Data**: Statistical analysis provides warnings

## Data Validation Examples

### **Valid CSV Sample**
```csv
Timestamp,Fill Time,B/S,Contract,filledQty,Avg Fill Price,Order ID,Status
2024-01-15 14:30:00,2024-01-15 14:30:15,B,MNQH5,2,16245.50,12345,Filled
2024-01-15 14:45:00,2024-01-15 14:45:10,S,MNQH5,2,16255.00,12346,Filled
```

### **Invalid CSV Examples**
```csv
# Missing required columns
Date,Side,Symbol,Quantity,Price
2024-01-15,B,MNQH5,2,16245.50

# Invalid data types
Timestamp,Fill Time,B/S,Contract,filledQty,Avg Fill Price,Order ID,Status
2024-01-15 14:30:00,2024-01-15 14:30:15,B,MNQH5,invalid,16245.50,12345,Filled
```

## Data Security and Privacy

### **Data Handling**
- **Temporary Processing**: Data not permanently stored
- **Memory-Only**: No disk writes except temporary upload
- **Session-Based**: Data cleared on session end
- **No Logging**: Trading data not logged to files

### **Privacy Considerations**
- **No Personal Info**: Only trading data processed
- **No Account Details**: No account numbers or personal identifiers
- **Anonymized**: UUIDs used for trade identification
- **Local Processing**: All analysis performed locally

## Performance Characteristics

### **Processing Speed**
- **CSV Loading**: ~50-100ms for typical files
- **Trade Construction**: ~10-20ms per 100 orders
- **Analysis**: ~5-10ms per 100 trades
- **JSON Serialization**: ~5-10ms per 100 trades

### **Memory Usage**
- **Linear Growth**: Memory scales with data size
- **Typical Usage**: ~1-2MB per 1000 trades
- **Peak Usage**: During initial CSV processing
- **Cleanup**: Automatic garbage collection

This data requirements documentation provides comprehensive guidance for understanding how TradeHabit processes trading data and what requirements must be met for successful analysis.