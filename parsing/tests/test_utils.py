import pytest
import pandas as pd
from datetime import datetime, timezone
from zoneinfo import ZoneInfo # Requires Python 3.9+

# Assuming PYTHONPATH is set up correctly for the import
from tradehabit.parsing.utils import normalize_timestamps_in_df, EXPECTED_TIMESTAMP_COLUMNS

# Define a consistent reference UTC timestamp for comparisons
REF_UTC_TS = datetime(2023, 1, 1, 15, 0, 0, tzinfo=timezone.utc) # 10:00 AM ET is 15:00 UTC (standard time)

# Helper to create sample DataFrames
def create_test_df(data):
    df = pd.DataFrame(data)
    # Ensure all potential timestamp columns are present as objects initially
    for col in EXPECTED_TIMESTAMP_COLUMNS:
        if col not in df.columns:
            df[col] = pd.Series(dtype='object')
    return df

def test_normalize_standard_format_naive():
    """Test standard naive 'YYYY-MM-DD HH:MM:SS' format (assumed America/New_York)."""
    data = {'ts': ["2023-01-01 10:00:00"], 'another_col': [1]}
    df = create_test_df(data)
    normalized_df = normalize_timestamps_in_df(df.copy()) # Use copy to avoid modifying original test data
    assert normalized_df['ts'].iloc[0] == REF_UTC_TS
    assert normalized_df['ts'].dt.tz == timezone.utc

def test_normalize_ms_format_naive():
    """Test naive 'YYYY-MM-DD HH:MM:SS.ffffff' format (assumed America/New_York)."""
    data = {'ts': ["2023-01-01 10:00:00.123456"], 'another_col': [1]}
    df = create_test_df(data)
    normalized_df = normalize_timestamps_in_df(df.copy())
    expected_ts_utc = REF_UTC_TS.replace(microsecond=123456)
    assert normalized_df['ts'].iloc[0] == expected_ts_utc
    assert normalized_df['ts'].dt.tz == timezone.utc

def test_normalize_already_utc():
    """Test with timestamps already in timezone-aware UTC."""
    data = {'entry_time': [REF_UTC_TS], 'another_col': [1]} # Using 'entry_time' column
    df = create_test_df(data)
    # Manually make the column datetime before passing, as if loaded from a source that preserves tz
    df['entry_time'] = pd.to_datetime(df['entry_time'], utc=True) 
    
    normalized_df = normalize_timestamps_in_df(df.copy())
    assert normalized_df['entry_time'].iloc[0] == REF_UTC_TS
    assert normalized_df['entry_time'].dt.tz == timezone.utc

def test_normalize_naive_datetime_objects():
    """Test with naive datetime objects (should be localized to ET then to UTC)."""
    naive_dt = datetime(2023, 1, 1, 10, 0, 0) # Represents 10:00 AM ET
    data = {'exit_time': [naive_dt], 'another_col': [1]} # Using 'exit_time' column
    df = create_test_df(data)
    
    normalized_df = normalize_timestamps_in_df(df.copy())
    assert normalized_df['exit_time'].iloc[0] == REF_UTC_TS
    assert normalized_df['exit_time'].dt.tz == timezone.utc

def test_normalize_other_timezone_aware_input():
    """Test with aware timestamps in a different timezone (e.g., PST). Should convert to UTC."""
    pst_tz = ZoneInfo("America/Los_Angeles")
    # 7:00 AM PST is 10:00 AM EST is 15:00 UTC
    pst_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=pst_tz) 
    data = {'ts': [pst_dt], 'another_col': [1]}
    df = create_test_df(data)
    # Manually make the column datetime before passing
    df['ts'] = pd.to_datetime(df['ts']) 

    normalized_df = normalize_timestamps_in_df(df.copy())
    assert normalized_df['ts'].iloc[0] == REF_UTC_TS
    assert normalized_df['ts'].dt.tz == timezone.utc

def test_normalize_non_timestamp_column_ignored():
    """Test that columns not in EXPECTED_TIMESTAMP_COLUMNS are ignored."""
    data = {'not_a_ts_col': ["some_string"], 'ts': ["2023-01-01 10:00:00"]}
    df = create_test_df(data)
    normalized_df = normalize_timestamps_in_df(df.copy())
    assert normalized_df['ts'].iloc[0] == REF_UTC_TS
    assert 'not_a_ts_col' in normalized_df # Column should still be there
    assert pd.api.types.is_string_dtype(normalized_df['not_a_ts_col']) # And its type unchanged

def test_normalize_missing_expected_column():
    """Test when an expected timestamp column is entirely missing from input DF."""
    # 'ts' is expected, but not in 'data'. create_test_df will add it as object dtype.
    data = {'some_other_data': [123]} 
    df = create_test_df(data)
    
    normalized_df = normalize_timestamps_in_df(df.copy())
    # The column 'ts' should still exist (as NaT if it was added by create_test_df and processed)
    # or remain as is if it wasn't auto-created and processed.
    # The function should not error out.
    assert 'ts' in normalized_df.columns 
    # If 'ts' was all NaNs/None initially, it should become NaT (Not a Time) after to_datetime
    if not df['ts'].dropna().empty: # If it had data that failed parsing
         assert pd.api.types.is_datetime64_any_dtype(normalized_df['ts'])
    # This test mainly ensures no crash. Content of 'ts' depends on initial state.
    # If it was created as empty object series, it might become NaT.
    assert normalized_df['some_other_data'].iloc[0] == 123


def test_normalize_empty_dataframe():
    """Test with an entirely empty DataFrame."""
    # create_test_df will add EXPECTED_TIMESTAMP_COLUMNS as empty Series of dtype 'object'
    df = create_test_df({}) 
    normalized_df = normalize_timestamps_in_df(df.copy())
    assert normalized_df.empty or all(pd.api.types.is_datetime64_any_dtype(normalized_df[col]) and normalized_df[col].isna().all() for col in EXPECTED_TIMESTAMP_COLUMNS if col in normalized_df)

def test_normalize_column_with_mixed_good_bad_data():
    """Test a column with some valid and some invalid/unparseable date strings."""
    data = {'ts': ["2023-01-01 10:00:00", "not-a-date", "2023-01-02 11:00:00"]}
    df = create_test_df(data)
    normalized_df = normalize_timestamps_in_df(df.copy())
    
    expected_ts1_utc = datetime(2023, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
    expected_ts3_utc = datetime(2023, 1, 2, 16, 0, 0, tzinfo=timezone.utc) # 11:00 ET
    
    assert normalized_df['ts'].iloc[0] == expected_ts1_utc
    assert pd.isna(normalized_df['ts'].iloc[1]) # 'not-a-date' should become NaT
    assert normalized_df['ts'].iloc[2] == expected_ts3_utc
    assert normalized_df['ts'].dt.tz == timezone.utc

def test_normalize_all_expected_columns_present():
    """Test when multiple expected timestamp columns are present."""
    data = {
        'ts': ["2023-01-01 10:00:00"],
        'entry_time': ["2023-01-01 10:01:00"], # 15:01 UTC
        'exit_time': ["2023-01-01 10:02:00"],  # 15:02 UTC
        'some_other_col': ["data"]
    }
    df = create_test_df(data)
    normalized_df = normalize_timestamps_in_df(df.copy())

    assert normalized_df['ts'].iloc[0] == datetime(2023,1,1,15,0,0, tzinfo=timezone.utc)
    assert normalized_df['entry_time'].iloc[0] == datetime(2023,1,1,15,1,0, tzinfo=timezone.utc)
    assert normalized_df['exit_time'].iloc[0] == datetime(2023,1,1,15,2,0, tzinfo=timezone.utc)
    assert normalized_df['ts'].dt.tz == timezone.utc
    assert normalized_df['entry_time'].dt.tz == timezone.utc
    assert normalized_df['exit_time'].dt.tz == timezone.utc
    assert normalized_df['some_other_col'].iloc[0] == "data" 