import pandas as pd
from typing import List

def normalize_timestamps_in_df(df: pd.DataFrame, source_column_name: str, target_column_name: str) -> pd.DataFrame:
    """
    Parses a specific timestamp column to datetime objects, normalizes them to UTC,
    and stores them in a new target column.

    Args:
        df: Input DataFrame.
        source_column_name: The name of the column containing timestamps to normalize.
        target_column_name: The name of the new column to store normalized timestamps.

    Returns:
        DataFrame with an added column containing UTC normalized timestamps.
        If the source column is not found or parsing fails for all rows,
        the target column might contain NaT.
    """
    if df is None or df.empty:
        return df

    if source_column_name not in df.columns:
        print(f"Warning: Source timestamp column '{source_column_name}' not found in DataFrame.")
        # Create an empty NaT column for the target if source is missing
        df_copy = df.copy()
        df_copy[target_column_name] = pd.NaT 
        return df_copy

    df_copy = df.copy()
    
    # Attempt to parse the timestamp column
    # Ensure the source column is treated as string first if it's mixed type or numeric
    if not pd.api.types.is_string_dtype(df_copy[source_column_name]) and not pd.api.types.is_datetime64_any_dtype(df_copy[source_column_name]):
        # Attempt to convert to string if it's not already, to handle potential numeric representations of dates/times
        # This can be risky if numbers are not actually date/time representations.
        # Consider if specific handling for Excel numbers is needed.
        # For now, a simple astype(str) if it's not obviously datetime already.
        try:
            df_copy[source_column_name] = df_copy[source_column_name].astype(str)
        except Exception as e:
            print(f"Warning: Could not convert source column '{source_column_name}' to string before datetime parsing. Error: {e}")
            df_copy[target_column_name] = pd.NaT
            return df_copy
            
    parsed_timestamps = pd.to_datetime(df_copy[source_column_name], errors='coerce')

    # Check if timestamps are timezone-aware
    if parsed_timestamps.dt.tz is None:
        # Timestamps are naive, localize to 'America/New_York' then convert to UTC
        try:
            df_copy[target_column_name] = parsed_timestamps.dt.tz_localize('America/New_York', ambiguous='infer', nonexistent='NaT').dt.tz_convert('UTC')
        except Exception as e:
            print(f"Warning: Could not localize timestamps from '{source_column_name}' assuming 'America/New_York'. Error: {e}. Fallback to UTC or NaT.")
            # Fallback: try to infer as UTC or leave as NaT
            try:
                df_copy[target_column_name] = parsed_timestamps.dt.tz_localize('UTC', ambiguous='infer', nonexistent='NaT')
            except Exception as e_utc:
                print(f"Warning: Direct UTC localization for '{source_column_name}' also failed. Error: {e_utc}")
                df_copy[target_column_name] = pd.NaT # Default to NaT if all fails
    else:
        # Timestamps are already timezone-aware, just convert to UTC
        df_copy[target_column_name] = parsed_timestamps.dt.tz_convert('UTC')
            
    if parsed_timestamps.isna().all() and not df_copy[source_column_name].isna().all(): # if source had data but all failed to parse
        print(f"Warning: All timestamps in column '{source_column_name}' failed to parse. Resulting '{target_column_name}' will be NaT.")
    
    # Ensure the target column exists even if all parsing failed to NaT
    if target_column_name not in df_copy.columns:
         df_copy[target_column_name] = pd.NaT

    return df_copy 