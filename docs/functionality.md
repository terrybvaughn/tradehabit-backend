# Functionality Overview

## Core Business Logic

### Primary Purpose
TradeHabit analyzes trading behavior to identify and quantify common trading mistakes. The application transforms raw NinjaTrader CSV exports into actionable behavioral insights through sophisticated statistical analysis and pattern recognition.

### Key Business Functions

#### 1. **Trading Mistake Detection**
The core business logic revolves around identifying five primary mistake categories:

- **No Stop-Loss Orders**: Trades executed without protective stops
- **Excessive Risk**: Position sizes exceeding statistical risk parameters  
- **Outsized Losses**: Losses exceeding μ + σ·(multiplier) on loss distribution
- **Revenge Trading**: Trades entered too quickly after losses
- **Risk Sizing Inconsistency**: High variation in position sizing

#### 2. **Statistical Analysis Engine**
- **Outlier Detection**: Uses Z-score methodology with configurable sigma multipliers
- **Distribution Analysis**: Calculates mean, standard deviation, and thresholds
- **Time Series Analysis**: Evaluates trading patterns over time
- **Performance Metrics**: Win rate, payoff ratios, and profitability analysis

#### 3. **Goal Tracking System**
- **Streak Monitoring**: Tracks consecutive mistake-free trades
- **Progress Metrics**: Measures improvement over time
- **Behavioral Goals**: Predefined and custom goal evaluation
- **Calendar and Trade-Based Tracking**: Flexible goal measurement options

## Key Modules and Functions

### Data Processing Pipeline (`parsing/`)

#### **order_loader.py**
```python
def load_orders(file_storage) -> pd.DataFrame
```
- **Purpose**: Loads and normalizes NinjaTrader CSV data
- **Process**:
  - Validates CSV format and required columns
  - Renames columns to internal naming conventions
  - Strips whitespace from string fields
  - Handles missing or malformed data gracefully
- **Output**: Normalized pandas DataFrame with standardized column names

#### **utils.py**
```python
def normalize_timestamps_in_df(df: pd.DataFrame) -> pd.DataFrame
```
- **Purpose**: Converts timestamps to UTC timezone
- **Process**:
  - Assumes America/New_York timezone for naive timestamps
  - Converts to UTC for consistent analysis
  - Handles parsing failures with fallback to NaT
- **Critical**: Ensures accurate time-based analysis for revenge trading detection

### Trade Construction (`analytics/trade_counter.py`)

#### **count_trades()**
```python
def count_trades(order_df: pd.DataFrame) -> tuple[list[Trade], dict]
```
- **Purpose**: Transforms order-level data into discrete trade objects
- **Algorithm**:
  - Maintains position tracking by symbol
  - Detects entries, scale-ins, and exits
  - Handles partial exits and complex position management
  - Creates Trade objects with complete metadata
- **Output**: List of Trade objects with entry/exit details

### Mistake Analysis Engine (`analytics/`)

#### **mistake_analyzer.py** - Central Orchestrator
```python
def analyze_all_mistakes(trades, order_df, sigma, k, sigma_risk)
```
- **Purpose**: Coordinates all mistake detection functions
- **Process**:
  1. Stop-loss analysis (highest priority)
  2. Excessive risk detection
  3. Outsized loss identification
  4. Revenge trading detection
  5. Risk sizing consistency evaluation
- **Design**: Modifies Trade objects in-place by adding mistakes to `mistakes` list

#### **stop_loss_analyzer.py** - Discipline Monitoring
```python
def analyze_trades_for_no_stop_mistake(trades, order_df)
```
- **Purpose**: Identifies trades without protective stop-loss orders
- **Algorithm**:
  - Scans 60-second window before trade entry
  - Detects stop-loss orders using order type and proximity
  - Handles OCO (One-Cancels-Other) scenarios
  - Flags trades lacking protective stops
- **Business Rule**: Essential for risk management discipline

#### **excessive_risk_analyzer.py** - Risk Outlier Detection
```python
def analyze_trades_for_excessive_risk(trades, sigma_risk=1.5)
```
- **Purpose**: Identifies trades with abnormally large risk exposure
- **Algorithm**:
  - Calculates risk_points from stop-loss distances
  - Computes mean and standard deviation of risk distribution
  - Flags trades exceeding mean + (sigma_risk × std_dev)
  - Provides statistical context for risk assessment
- **Business Rule**: Prevents position sizing mistakes

#### **outsized_loss_analyzer.py** - Loss Control
```python
def analyze_trades_for_outsized_loss(trades, sigma_multiplier=1.0)
```
- **Purpose**: Identifies losses exceeding acceptable thresholds
- **Algorithm**:
  - Analyzes points_lost distribution for losing trades
  - Calculates threshold using mean + (sigma × std_dev)
  - Flags losses exceeding statistical expectations
  - Quantifies excess loss contribution
- **Business Rule**: Loss consistency and capital preservation

#### **revenge_analyzer.py** - Emotional Trading Detection
```python
def analyze_trades_for_revenge(trades, k=1.0)
```
- **Purpose**: Identifies trades taken too quickly after losses
- **Algorithm**:
  - Calculates median hold time from historical trades
  - Defines "too quick" as k × median_hold_time
  - Scans for trades entered within revenge window after losses
  - Analyzes performance impact of revenge trading
- **Business Rule**: Prevents emotional decision-making

#### **risk_sizing_analyzer.py** - Consistency Monitoring
```python
def analyze_trades_for_risk_sizing_consistency(trades, vr_threshold=0.35)
```
- **Purpose**: Evaluates consistency of position sizing
- **Algorithm**:
  - Calculates risk_points from stop-loss distances
  - Computes coefficient of variation (std_dev / mean)
  - Flags high variation indicating inconsistent sizing
  - Provides risk sizing statistics
- **Business Rule**: Ensures systematic risk management

### Insights Generation (`analytics/insights.py`)

#### **build_insights()**
```python
def build_insights(trade_objs, order_df) -> dict
```
- **Purpose**: Creates prioritized behavioral insights using decision-tree logic
- **Algorithm**:
  - Evaluates mistake severity and frequency
  - Prioritizes insights based on impact and actionability
  - Generates plain-English diagnostic messages
  - Provides statistical context for each insight
- **Output**: Comprehensive insights report with prioritized recommendations

### Goal Tracking (`analytics/goal_tracker.py`)

#### **evaluate_goal()**
```python
def evaluate_goal(trades, mistake_types, goal_target, metric, start_date=None)
```
- **Purpose**: Tracks progress toward behavioral improvement goals
- **Algorithm**:
  - Filters trades by date range and mistake types
  - Calculates current and best streaks
  - Supports both trade-based and calendar-based metrics
  - Provides progress percentage toward goals
- **Business Rule**: Measurable behavioral improvement tracking

#### **generate_goal_report()**
```python
def generate_goal_report(trades) -> dict
```
- **Purpose**: Provides comprehensive goal progress reporting
- **Includes**:
  - Clean trades goal (no mistakes)
  - Risk management goal (no excessive risk)
  - Revenge trading avoidance goal
  - Current and best streak statistics
- **Output**: Complete goal dashboard data

## Module Interactions

### Data Flow Sequence
1. **Upload** → `app.py` receives CSV file
2. **Validation** → `order_loader.py` validates and normalizes data
3. **Trade Construction** → `trade_counter.py` creates Trade objects
4. **Analysis** → `mistake_analyzer.py` orchestrates all analyzers
5. **Insights** → `insights.py` generates prioritized feedback
6. **Goals** → `goal_tracker.py` tracks improvement progress
7. **Response** → `app.py` serializes and returns JSON

### Key Integration Points

#### **Flask API Layer** (`app.py`)
- **Purpose**: Orchestrates business logic and provides HTTP interface
- **Key Functions**:
  - File upload handling and validation
  - Analysis orchestration and result serialization
  - Settings management for configurable thresholds
  - Error handling and user feedback
- **Integration**: Calls all analytics modules and manages global state

#### **Global State Management**
```python
trade_objs = []  # List of Trade objects
order_df = None  # Original order DataFrame
THRESHOLDS = {   # Configurable analysis parameters
    "k": 1.0,
    "sigma_loss": 1.0,
    "sigma_risk": 1.5,
    "vr": 0.35,
}
```

#### **Cross-Module Communication**
- **Trade Objects**: Shared data structure modified by multiple analyzers
- **Order DataFrame**: Preserved for time-based analysis
- **Threshold Configuration**: Global parameters affecting all analyzers
- **Error Handling**: Centralized through `errors.py`

## Utility Functions

### **Statistical Utilities**
- **Mean and Standard Deviation**: Using `statistics` module
- **Z-score Calculations**: For outlier detection
- **Coefficient of Variation**: For consistency measurement
- **Population vs Sample Statistics**: Appropriate statistical measures

### **Time-Based Utilities**
- **Timestamp Normalization**: UTC conversion and timezone handling
- **Time Window Analysis**: For revenge trading detection
- **Duration Calculations**: Hold time and trading frequency analysis

### **Data Validation**
- **Column Validation**: Required field checking
- **Type Conversion**: Safe numeric and datetime conversion
- **Quality Checks**: Data integrity verification

## Business Rules Implementation

### **Risk Management Rules**
- Traders should use stop-loss orders on all positions
- Position sizes should be consistent with risk parameters
- Losses should not exceed statistical expectations
- Risk exposure should be proportional to account size

### **Behavioral Rules**
- Avoid trading immediately after losses (revenge trading)
- Maintain consistent position sizing methodology
- Focus on process improvement over profit maximization
- Track measurable behavioral goals

### **Statistical Rules**
- Use population standard deviation for threshold calculations
- Apply configurable sigma multipliers for personalization
- Prioritize insights based on frequency and impact
- Provide statistical context for all recommendations

This functionality framework provides comprehensive behavioral analysis capabilities while maintaining flexibility for different trading styles and risk preferences.