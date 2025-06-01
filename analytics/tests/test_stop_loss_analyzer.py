import pytest
import pandas as pd
from datetime import datetime, timezone

from tradehabit.models.trade import Trade # Assuming PYTHONPATH is set for tradehabit.models
from analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake, _get_relevant_orders_for_trade

# Helper function to create a sample trade for testing
def create_sample_trade(
    symbol="MSFT", 
    side="Buy", 
    entry_time=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
    entry_price=100.0,
    entry_qty=10,
    exit_time=datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
    exit_price=101.0,
    exit_qty=10,
    mistakes=None
) -> Trade:
    if mistakes is None:
        mistakes = []
    return Trade(
        symbol=symbol,
        side=side,
        entry_time=entry_time,
        entry_price=entry_price,
        entry_qty=entry_qty,
        exit_time=exit_time,
        exit_price=exit_price,
        exit_qty=exit_qty,
        mistakes=list(mistakes) # Ensure it's a new list instance
    )

# --- Acceptance Criteria Tests --- 

# AC1: No Stop Order Placed
def test_ac1_no_stop_order_placed_buy_trade():
    """Test AC1: No stop order placed for a Buy trade."""
    trade = create_sample_trade(side="Buy") 
    # Empty DataFrame means no orders at all, hence no stop
    raw_orders_df = pd.DataFrame(columns=['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price'])
    
    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes

def test_ac1_no_stop_order_placed_sell_trade():
    """Test AC1: No stop order placed for a Sell trade."""
    trade = create_sample_trade(side="Sell", entry_price=100.0, exit_price=99.0)
    raw_orders_df = pd.DataFrame(columns=['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price'])
    
    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes

def test_ac1_irrelevant_orders_present_no_stop():
    """Test AC1: Other irrelevant orders present, but still no valid stop."""
    trade = create_sample_trade(side="Buy")
    # Orders present, but none are stops, or they don't meet criteria
    orders_data = [
        # A Limit order, not a stop
        {'symbol': "MSFT", 'side': "Sell", 'qty': 5, 'price': 102.0, 'ts': datetime(2023,1,1,10,5,0, tzinfo=timezone.utc), 'Type': "Limit", 'Status': "Filled", 'Stop Price': None},
        # A Buy order, not a protective stop for a Buy trade
        {'symbol': "MSFT", 'side': "Buy", 'qty': 2, 'price': 99.0, 'ts': datetime(2023,1,1,10,10,0, tzinfo=timezone.utc), 'Type': "Market", 'Status': "Filled", 'Stop Price': None},
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    # Ensure all expected columns from analyze_trades_for_no_stop_mistake are present
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = None # Add missing columns with None, adjust type if necessary
    # Coerce specific types if necessary based on how analyze_trades_for_no_stop_mistake uses them
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes

# AC2: Valid Stop Order Placed
def test_ac2_valid_stop_order_placed_buy_trade_working_stop():
    """Test AC2: Valid 'Working' Sell Stop order for a Buy trade."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(side="Buy", entry_time=trade_entry_time, entry_price=100.0)
    
    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, # Price is not used for market execution of stop
         'ts': trade_entry_time + pd.Timedelta(seconds=1), 
         'Type': "Stop", 'Status': "Working", 'Stop Price': 99.0}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = pd.NA # Use pd.NA for missing data to be explicit
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns: # Fill Price for Market/Limit orders
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes

def test_ac2_valid_stop_order_placed_sell_trade_filled_stop_limit():
    """Test AC2: Valid 'Filled' Buy Stop Limit order for a Sell trade."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(side="Sell", entry_time=trade_entry_time, entry_price=150.0, exit_price=155.0)
    
    orders_data = [
        {'symbol': "MSFT", 'side': "Buy", 'qty': 10, 'price': 155.0, # Limit price for the stop limit
         'ts': trade_entry_time + pd.Timedelta(minutes=1),
         'Type': "Stop Limit", 'Status': "Filled", 'Stop Price': 154.0}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = pd.NA
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns:
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes

# AC3: OCO Cancellation - Profit Target Hit
def test_ac3_oco_cancellation_profit_target_hit():
    """Test AC3: Cancelled stop with a simultaneously filled profit target (OCO)."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc) # Trade exit by other means
    trade = create_sample_trade(
        side="Buy", 
        entry_time=trade_entry_time, 
        entry_price=100.0,
        exit_time=trade_exit_time,
        exit_price=102.0 # Exit price if trade closed by target
    )

    oco_event_time = trade_entry_time + pd.Timedelta(minutes=5)
    stop_cancellation_time = oco_event_time
    target_fill_time = oco_event_time + pd.Timedelta(milliseconds=50)

    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_cancellation_time, 
         'Type': "Stop", 'Status': "Cancelled", 'Stop Price': 99.0},
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': 102.0, 
         'ts': target_fill_time, 
         'Type': "Limit", 'Status': "Filled", 'Stop Price': None}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = pd.NA
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns:
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes,
           f"Mistake found: {analyzed_trades[0].mistakes} when OCO should prevent it."

# --- Placeholder for AC4 onwards ---
def test_ac4_oco_cancellation_no_profit_target_hit():
    """Test AC4: OCO-like cancellation but profit target NOT hit (filled outside OCO window)."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(
        side="Buy", 
        entry_time=trade_entry_time, 
        entry_price=100.0,
        exit_time=trade_exit_time,
        exit_price=102.0 
    )

    stop_cancellation_time = trade_entry_time + pd.Timedelta(minutes=5)
    # Target fill time significantly outside the 250ms window (e.g., 1 second later)
    target_fill_time = stop_cancellation_time + pd.Timedelta(seconds=1)

    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_cancellation_time, 
         'Type': "Stop", 'Status': "Cancelled", 'Stop Price': 99.0},
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': 102.0, 
         'ts': target_fill_time, 
         'Type': "Limit", 'Status': "Filled", 'Stop Price': None}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = pd.NA
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns:
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes,
           f"Mistake NOT found: {analyzed_trades[0].mistakes} when cancelled stop outside OCO window should trigger it."

def test_ac4_oco_cancellation_no_profit_target_order_at_all():
    """Test AC4: Cancelled stop and no corresponding profit target order exists."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(
        side="Sell", 
        entry_time=trade_entry_time, 
        entry_price=200.0,
        exit_time=trade_exit_time,
        exit_price=198.0 
    )

    stop_cancellation_time = trade_entry_time + pd.Timedelta(minutes=10)

    orders_data = [
        # Cancelled stop for a Sell trade (so stop is a Buy)
        {'symbol': "MSFT", 'side': "Buy", 'qty': 10, 'price': None, 
         'ts': stop_cancellation_time, 
         'Type': "Stop", 'Status': "Cancelled", 'Stop Price': 202.0},
        # No other orders, specifically no Limit order that could be a profit target
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    # Ensure all columns are present, even if this specific test doesn't use them all
    # This prevents issues if the main code expects columns not in minimal test data
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            # Use pd.NA for type flexibility, or more specific types if known (e.g., float for price)
            if col in ['price', 'Stop Price']:
                raw_orders_df[col] = pd.Series(dtype='float64')
            elif col == 'ts':
                raw_orders_df[col] = pd.Series(dtype='datetime64[ns, UTC]')
            else:
                raw_orders_df[col] = pd.NA
    
    # Coerce types after ensuring columns exist
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns:
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    if 'ts' in raw_orders_df.columns:
        raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)


    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes,
           f"Mistake NOT found for cancelled stop with no profit target. Mistakes: {analyzed_trades[0].mistakes}"

def test_ac5_stop_placed_before_entry():
    """Test AC5: Stop order placed *before* trade entry (should not be considered)."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(
        side="Buy", 
        entry_time=trade_entry_time, 
        entry_price=100.0,
        exit_time=trade_exit_time,
        exit_price=101.0
    )

    # Stop order placed 1 minute BEFORE the trade entry
    stop_order_time = trade_entry_time - pd.Timedelta(minutes=1)

    orders_data = [
        # This stop is valid in terms of price and side, but placed too early
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 
         'Type': "Stop", 'Status': "Working", 'Stop Price': 99.0}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    expected_cols = ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']
    for col in expected_cols:
        if col not in raw_orders_df.columns:
            raw_orders_df[col] = pd.NA
    if 'Stop Price' in raw_orders_df.columns:
        raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    if 'price' in raw_orders_df.columns:
        raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    if 'ts' in raw_orders_df.columns:
        raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes,
           f"Mistake NOT found. Stop placed before entry should be ignored. Mistakes: {analyzed_trades[0].mistakes}"

def test_ac6_stop_price_not_a_loss_buy_trade():
    """Test AC6: Stop price for a Buy trade is not a loss (e.g., at or above entry)."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    entry_price = 100.0
    trade = create_sample_trade(
        side="Buy", 
        entry_time=trade_entry_time, 
        entry_price=entry_price,
        exit_time=trade_exit_time,
        exit_price=101.0 
    )

    stop_order_time = trade_entry_time + pd.Timedelta(seconds=30)

    # Scenario 1: Stop price IS EQUAL to entry price (not a loss-making stop)
    orders_data_at_entry = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 
         'Type': "Stop", 'Status': "Working", 'Stop Price': entry_price} # Stop Price == Entry Price
    ]
    raw_orders_df_at_entry = pd.DataFrame(orders_data_at_entry)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df_at_entry.columns: raw_orders_df_at_entry[col] = pd.NA
    raw_orders_df_at_entry['Stop Price'] = pd.to_numeric(raw_orders_df_at_entry['Stop Price'], errors='coerce')
    raw_orders_df_at_entry['price'] = pd.to_numeric(raw_orders_df_at_entry['price'], errors='coerce')
    raw_orders_df_at_entry['ts'] = pd.to_datetime(raw_orders_df_at_entry['ts'], errors='coerce', utc=True)

    analyzed_trades_at_entry = analyze_trades_for_no_stop_mistake([trade], raw_orders_df_at_entry)
    assert len(analyzed_trades_at_entry) == 1
    assert "no stop-loss order" in analyzed_trades_at_entry[0].mistakes,
           f"AC6-S1: Mistake NOT found. Buy trade stop at entry price. Mistakes: {analyzed_trades_at_entry[0].mistakes}"
    trade.mistakes = [] # Reset mistakes for next scenario

    # Scenario 2: Stop price IS GREATER than entry price (break-even or profit stop, not initial loss protection)
    orders_data_above_entry = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 
         'Type': "Stop", 'Status': "Working", 'Stop Price': entry_price + 1.0} # Stop Price > Entry Price
    ]
    raw_orders_df_above_entry = pd.DataFrame(orders_data_above_entry)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df_above_entry.columns: raw_orders_df_above_entry[col] = pd.NA
    raw_orders_df_above_entry['Stop Price'] = pd.to_numeric(raw_orders_df_above_entry['Stop Price'], errors='coerce')
    raw_orders_df_above_entry['price'] = pd.to_numeric(raw_orders_df_above_entry['price'], errors='coerce')
    raw_orders_df_above_entry['ts'] = pd.to_datetime(raw_orders_df_above_entry['ts'], errors='coerce', utc=True)
    
    analyzed_trades_above_entry = analyze_trades_for_no_stop_mistake([trade], raw_orders_df_above_entry)
    assert len(analyzed_trades_above_entry) == 1
    assert "no stop-loss order" in analyzed_trades_above_entry[0].mistakes,
           f"AC6-S2: Mistake NOT found. Buy trade stop above entry price. Mistakes: {analyzed_trades_above_entry[0].mistakes}"

def test_ac7_stop_price_not_a_loss_sell_trade():
    """Test AC7: Stop price for a Sell trade is not a loss (e.g., at or below entry)."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    entry_price = 200.0
    trade = create_sample_trade(
        side="Sell", 
        entry_time=trade_entry_time, 
        entry_price=entry_price,
        exit_time=trade_exit_time,
        exit_price=199.0 
    )

    stop_order_time = trade_entry_time + pd.Timedelta(seconds=30)

    # Scenario 1: Stop price IS EQUAL to entry price
    orders_data_at_entry = [
        {'symbol': "MSFT", 'side': "Buy", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 
         'Type': "Stop", 'Status': "Working", 'Stop Price': entry_price} # Stop Price == Entry Price
    ]
    raw_orders_df_at_entry = pd.DataFrame(orders_data_at_entry)
    # Ensure necessary columns and types
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df_at_entry.columns: raw_orders_df_at_entry[col] = pd.NA
    raw_orders_df_at_entry['Stop Price'] = pd.to_numeric(raw_orders_df_at_entry['Stop Price'], errors='coerce')
    raw_orders_df_at_entry['price'] = pd.to_numeric(raw_orders_df_at_entry['price'], errors='coerce')
    raw_orders_df_at_entry['ts'] = pd.to_datetime(raw_orders_df_at_entry['ts'], errors='coerce', utc=True)

    analyzed_trades_at_entry = analyze_trades_for_no_stop_mistake([trade], raw_orders_df_at_entry)
    assert len(analyzed_trades_at_entry) == 1
    assert "no stop-loss order" in analyzed_trades_at_entry[0].mistakes,
           f"AC7-S1: Mistake NOT found. Sell trade stop at entry price. Mistakes: {analyzed_trades_at_entry[0].mistakes}"
    trade.mistakes = [] # Reset for next scenario

    # Scenario 2: Stop price IS LESS than entry price
    orders_data_below_entry = [
        {'symbol': "MSFT", 'side': "Buy", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 
         'Type': "Stop", 'Status': "Working", 'Stop Price': entry_price - 1.0} # Stop Price < Entry Price
    ]
    raw_orders_df_below_entry = pd.DataFrame(orders_data_below_entry)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df_below_entry.columns: raw_orders_df_below_entry[col] = pd.NA
    raw_orders_df_below_entry['Stop Price'] = pd.to_numeric(raw_orders_df_below_entry['Stop Price'], errors='coerce')
    raw_orders_df_below_entry['price'] = pd.to_numeric(raw_orders_df_below_entry['price'], errors='coerce')
    raw_orders_df_below_entry['ts'] = pd.to_datetime(raw_orders_df_below_entry['ts'], errors='coerce', utc=True)

    analyzed_trades_below_entry = analyze_trades_for_no_stop_mistake([trade], raw_orders_df_below_entry)
    assert len(analyzed_trades_below_entry) == 1
    assert "no stop-loss order" in analyzed_trades_below_entry[0].mistakes,
           f"AC7-S2: Mistake NOT found. Sell trade stop below entry price. Mistakes: {analyzed_trades_below_entry[0].mistakes}"

# --- OCO Timing Variation Tests ---
def test_oco_timing_boundary_hit():
    """Test OCO: Profit target filled exactly at the 250ms boundary. Should be a hit.
    Note: If data timestamps only have second precision, this test might behave 
    identically to a 0ms difference if 250ms truncates to the same second.
    """
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(side="Buy", entry_time=trade_entry_time, entry_price=100.0)
    
    stop_cancellation_time = trade_entry_time + pd.Timedelta(minutes=5)
    # Target fill time exactly at the 250ms window boundary
    target_fill_time = stop_cancellation_time + pd.Timedelta(milliseconds=250)

    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_cancellation_time, 'Type': "Stop", 'Status': "Cancelled", 'Stop Price': 99.0},
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': 102.0, 
         'ts': target_fill_time, 'Type': "Limit", 'Status': "Filled", 'Stop Price': None}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    # Ensure necessary columns and types
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df.columns: raw_orders_df[col] = pd.NA
    raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes,
           f"OCO boundary HIT (250ms) failed. Mistakes: {analyzed_trades[0].mistakes}"

def test_oco_timing_boundary_miss():
    """Test OCO: Profit target filled just outside the 250ms boundary (at 251ms).
    Should be a miss. Note: Timestamp precision issues as with the boundary hit test.
    """
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(side="Buy", entry_time=trade_entry_time, entry_price=100.0)
    
    stop_cancellation_time = trade_entry_time + pd.Timedelta(minutes=5)
    # Target fill time just outside the 250ms window boundary
    target_fill_time = stop_cancellation_time + pd.Timedelta(milliseconds=251)

    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_cancellation_time, 'Type': "Stop", 'Status': "Cancelled", 'Stop Price': 99.0},
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': 102.0, 
         'ts': target_fill_time, 'Type': "Limit", 'Status': "Filled", 'Stop Price': None}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df.columns: raw_orders_df[col] = pd.NA
    raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" in analyzed_trades[0].mistakes,
           f"OCO boundary MISS (251ms) failed. Mistakes: {analyzed_trades[0].mistakes}"

# --- Timestamp Edge Case Tests (Sub-task 5.3) ---
def test_ts_stop_exactly_at_trade_entry():
    """Test TS Edge: Valid stop order placed exactly at trade entry time."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc) # Trade lasts 5 mins
    trade = create_sample_trade(
        side="Buy", 
        entry_time=trade_entry_time, 
        entry_price=100.0,
        exit_time=trade_exit_time,
        exit_price=101.0
    )
    
    # Stop order placed exactly at trade entry time
    stop_order_time = trade_entry_time 

    orders_data = [
        {'symbol': "MSFT", 'side': "Sell", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 'Type': "Stop", 'Status': "Working", 'Stop Price': 99.0}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df.columns: raw_orders_df[col] = pd.NA
    raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes,
           f"Stop at entry time not considered valid. Mistakes: {analyzed_trades[0].mistakes}"

def test_ts_stop_exactly_at_trade_exit():
    """Test TS Edge: Valid stop order placed exactly at trade exit time."""
    trade_entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    trade_exit_time = datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(
        side="Sell", 
        entry_time=trade_entry_time, 
        entry_price=200.0,
        exit_time=trade_exit_time,
        exit_price=199.0 
    )
    
    # Stop order placed exactly at trade exit time
    stop_order_time = trade_exit_time

    orders_data = [
        {'symbol': "MSFT", 'side': "Buy", 'qty': 10, 'price': None, 
         'ts': stop_order_time, 'Type': "Stop", 'Status': "Working", 'Stop Price': 201.0}
    ]
    raw_orders_df = pd.DataFrame(orders_data)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in raw_orders_df.columns: raw_orders_df[col] = pd.NA
    raw_orders_df['Stop Price'] = pd.to_numeric(raw_orders_df['Stop Price'], errors='coerce')
    raw_orders_df['price'] = pd.to_numeric(raw_orders_df['price'], errors='coerce')
    raw_orders_df['ts'] = pd.to_datetime(raw_orders_df['ts'], errors='coerce', utc=True)

    analyzed_trades = analyze_trades_for_no_stop_mistake([trade], raw_orders_df)
    
    assert len(analyzed_trades) == 1
    assert "no stop-loss order" not in analyzed_trades[0].mistakes,
           f"Stop at exit time not considered valid. Mistakes: {analyzed_trades[0].mistakes}"

# --- Unit Tests for Helper Functions (Sub-task 5.5) ---

# Unit tests for _get_relevant_orders_for_trade
def test_get_relevant_orders_basic_case():
    """Test _get_relevant_orders_for_trade: Basic case with matching orders."""
    entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(symbol="AAPL", entry_time=entry_time, exit_time=exit_time)

    orders_data = [
        # Relevant order
        {'symbol': "AAPL", 'ts': entry_time + pd.Timedelta(minutes=5), 'Type': "Limit", 'Status': "Filled"},
        # Irrelevant symbol
        {'symbol': "MSFT", 'ts': entry_time + pd.Timedelta(minutes=10), 'Type': "Limit", 'Status': "Filled"},
        # Relevant symbol, but outside time window (before)
        {'symbol': "AAPL", 'ts': entry_time - pd.Timedelta(minutes=5), 'Type': "Stop", 'Status': "Working"},
        # Relevant symbol, but outside time window (after)
        {'symbol': "AAPL", 'ts': exit_time + pd.Timedelta(minutes=5), 'Type': "Stop", 'Status': "Cancelled"},
        # Relevant order - exactly at entry time
        {'symbol': "AAPL", 'ts': entry_time, 'Type': "Market", 'Status': "Filled"},
        # Relevant order - exactly at exit time
        {'symbol': "AAPL", 'ts': exit_time, 'Type': "Limit", 'Status': "Filled"},
    ]
    all_raw_orders_df = pd.DataFrame(orders_data)
    # Ensure standard columns exist
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in all_raw_orders_df.columns: all_raw_orders_df[col] = pd.NA
    all_raw_orders_df['ts'] = pd.to_datetime(all_raw_orders_df['ts'], utc=True)

    relevant_orders = _get_relevant_orders_for_trade(trade, all_raw_orders_df)
    assert len(relevant_orders) == 3
    assert all(relevant_orders['symbol'] == "AAPL")
    assert all(relevant_orders['ts'] >= entry_time)
    assert all(relevant_orders['ts'] <= exit_time)

def test_get_relevant_orders_no_symbol_match():
    """Test _get_relevant_orders_for_trade: No orders match the trade symbol."""
    trade = create_sample_trade(symbol="GOOG") # Trade is GOOG
    orders_data = [
        {'symbol': "AAPL", 'ts': datetime(2023,1,1,10,5,0, tzinfo=timezone.utc), 'Type': "Limit"},
        {'symbol': "MSFT", 'ts': datetime(2023,1,1,10,10,0, tzinfo=timezone.utc), 'Type': "Stop"},
    ]
    all_raw_orders_df = pd.DataFrame(orders_data)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in all_raw_orders_df.columns: all_raw_orders_df[col] = pd.NA
    all_raw_orders_df['ts'] = pd.to_datetime(all_raw_orders_df['ts'], utc=True)

    relevant_orders = _get_relevant_orders_for_trade(trade, all_raw_orders_df)
    assert len(relevant_orders) == 0

def test_get_relevant_orders_no_time_match():
    """Test _get_relevant_orders_for_trade: Orders match symbol but not time window."""
    entry_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    exit_time = datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    trade = create_sample_trade(symbol="AAPL", entry_time=entry_time, exit_time=exit_time)

    orders_data = [
        {'symbol': "AAPL", 'ts': entry_time - pd.Timedelta(minutes=1), 'Type': "Limit"}, # Before
        {'symbol': "AAPL", 'ts': exit_time + pd.Timedelta(minutes=1), 'Type': "Stop"},   # After
    ]
    all_raw_orders_df = pd.DataFrame(orders_data)
    for col in ['symbol', 'side', 'qty', 'price', 'ts', 'Type', 'Status', 'Stop Price']:
        if col not in all_raw_orders_df.columns: all_raw_orders_df[col] = pd.NA
    all_raw_orders_df['ts'] = pd.to_datetime(all_raw_orders_df['ts'], utc=True)

    relevant_orders = _get_relevant_orders_for_trade(trade, all_raw_orders_df)
    assert len(relevant_orders) == 0

def test_get_relevant_orders_empty_input_df():
    """Test _get_relevant_orders_for_trade: Input DataFrame is empty."""
    trade = create_sample_trade()
    all_raw_orders_df = pd.DataFrame(columns=['symbol', 'ts', 'Type', 'Status', 'Stop Price'])
    # Ensure ts is datetime even if empty, to avoid dtype issues in the function if it assumes datetime
    all_raw_orders_df['ts'] = pd.to_datetime(all_raw_orders_df['ts'], utc=True)
    all_raw_orders_df['symbol'] = all_raw_orders_df['symbol'].astype("object") # or string if appropriate

    relevant_orders = _get_relevant_orders_for_trade(trade, all_raw_orders_df)
    assert len(relevant_orders) == 0 