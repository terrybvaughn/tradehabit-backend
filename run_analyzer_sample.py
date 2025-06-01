import pandas as pd
import io
import argparse

from parsing.trade_counter import normalize_and_prepare_orders_df, count_trades
from analytics.stop_loss_analyzer import analyze_trades_for_no_stop_mistake
from models.trade import Trade

# Sample CSV data based on user-provided format and scenarios for testing
SAMPLE_CSV_DATA = \
"""orderId,Account,Order ID,B/S,Contract,Product,Product Description,avgPrice,filledQty,Fill Time,lastCommandId,Status,_priceFormat,_priceFormatType,_tickSize,spreadDefinitionId,Version ID,Timestamp,Date,Quantity,Text,Type,Limit Price,Stop Price,decimalLimit,decimalStop,Filled Qty,Avg Fill Price,decimalFillAvg
# Trade 1: Buy MNQ, exit with a manual limit order, no stop placed initially
1001,TestAcc,1001,Buy,MNQZ4,MNQ,Micro NASDAQ,18000.00,1,12/03/2024 10:00:00,1001,Filled,-2,0,0.25,,1001,12/03/2024 10:00:00,12/3/24,1,,Market,,,18000.00,,1,18000.00,18000.00
1002,TestAcc,1002,Sell,MNQZ4,MNQ,Micro NASDAQ,18010.00,1,12/03/2024 10:05:00,1002,Filled,-2,0,0.25,,1002,12/03/2024 10:05:00,12/3/24,1,,Limit,18010.00,,18010.00,,1,18010.00,18010.00

# Trade 2: Buy ES, place a valid stop, stop gets filled
2001,TestAcc,2001,Buy,ESZ4,ES,E-mini S&P,5000.00,1,12/03/2024 10:10:00,2001,Filled,-2,0,0.25,,2001,12/03/2024 10:10:00,12/3/24,1,,Market,,,5000.00,,1,5000.00,5000.00
2002,TestAcc,2002,Sell,ESZ4,ES,E-mini S&P,,,,,2002,Working,-2,0,0.25,,2002,12/03/2024 10:10:01,12/3/24,1,,Stop,,4995.00,,4995.00,,,,
2003,TestAcc,2003,Sell,ESZ4,ES,E-mini S&P,4995.00,1,12/03/2024 10:15:00,2002,Filled,-2,0,0.25,,2002,12/03/2024 10:15:00,12/3/24,1,,Stop,,4995.00,,4995.00,1,4995.00,4995.00

# Trade 3: Sell MNQ, place a stop, cancel stop, profit target hit (OCO-like)
3001,TestAcc,3001,Sell,MNQZ4,MNQ,Micro NASDAQ,18050.00,2,12/03/2024 10:20:00,3001,Filled,-2,0,0.25,,3001,12/03/2024 10:20:00,12/3/24,2,,Market,,,18050.00,,2,18050.00,18050.00
3002,TestAcc,3002,Buy,MNQZ4,MNQ,Micro NASDAQ,,,,,3002,Working,-2,0,0.25,,3002,12/03/2024 10:20:01,12/3/24,2,,Stop,,18055.00,,18055.00,,,,
3003,TestAcc,3003,Buy,MNQZ4,MNQ,Micro NASDAQ,,,,,3002,Canceled,-2,0,0.25,,3002,12/03/2024 10:22:00,12/3/24,2,,Stop,,18055.00,,18055.00,,,,
3004,TestAcc,3004,Buy,MNQZ4,MNQ,Micro NASDAQ,18040.00,2,12/03/2024 10:22:00,3004,Filled,-2,0,0.25,,3004,12/03/2024 10:22:00,12/3/24,2,,Limit,18040.00,,18040.00,,2,18040.00,18040.00

# Trade 4: Sell ES, no stop placed at all, trade closed manually
4001,TestAcc,4001,Sell,ESZ4,ES,E-mini S&P,5010.00,1,12/03/2024 10:30:00,4001,Filled,-2,0,0.25,,4001,12/03/2024 10:30:00,12/3/24,1,,Market,,,5010.00,,1,5010.00,5010.00
4002,TestAcc,4002,Buy,ESZ4,ES,E-mini S&P,5005.00,1,12/03/2024 10:35:00,4002,Filled,-2,0,0.25,,4002,12/03/2024 10:35:00,12/3/24,1,,Limit,5005.00,,5005.00,,1,5005.00,5005.00
"""

def main():
    parser = argparse.ArgumentParser(description="Analyze trade data for 'no stop-loss order' mistakes.")
    parser.add_argument(
        "csv_file", 
        type=str, 
        nargs='?', 
        help="Path to the CSV file containing order data. Uses sample data if not provided."
    )
    args = parser.parse_args()

    raw_orders_df: pd.DataFrame
    if args.csv_file:
        print(f"Loading CSV data from: {args.csv_file}...")
        try:
            raw_orders_df = pd.read_csv(args.csv_file)
        except FileNotFoundError:
            print(f"Error: File not found at {args.csv_file}")
            return
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return
    else:
        print("No CSV file provided, using sample data...")
        csv_file_like_object = io.StringIO(SAMPLE_CSV_DATA)
        raw_orders_df = pd.read_csv(csv_file_like_object)

    print("Normalizing and preparing orders...")
    # raw_orders_df is the DataFrame directly from pd.read_csv()
    # normalize_and_prepare_orders_df will handle renaming, type conversion, and ts normalization
    final_orders_df = normalize_and_prepare_orders_df(raw_orders_df)

    if final_orders_df is None or final_orders_df.empty:
        print("Order processing resulted in an empty DataFrame. Cannot proceed.")
        return
    if 'ts' not in final_orders_df.columns or not pd.api.types.is_datetime64_any_dtype(final_orders_df['ts'].dtype):
        print("Critical error: 'ts' column is missing or not datetime after normalization. Cannot proceed.")
        # print(final_orders_df.info()) # for debugging
        return

    print("Counting trades...")
    trades, _ = count_trades(final_orders_df) # count_trades now expects the processed DataFrame
    
    print(f"Found {len(trades)} trades.")
    if not trades:
        print("No trades identified. Cannot perform stop-loss analysis.")
        return

    print("Analyzing trades for 'no stop-loss order' mistakes...")
    analyzed_trades = analyze_trades_for_no_stop_mistake(trades, final_orders_df)

    mistake_count = 0
    print("\n--- Analysis Results ---")
    if not analyzed_trades:
        print("No trades were analyzed or returned from analyzer.")
    
    flagged_trades_details = []
    for i, trade_obj in enumerate(analyzed_trades):
        if "no stop-loss order" in trade_obj.mistakes:
            mistake_count += 1
            # Convert UTC timestamps to America/New_York for display
            display_entry_time = trade_obj.entry_time.tz_convert('America/New_York') if trade_obj.entry_time.tzinfo else trade_obj.entry_time
            display_exit_time = trade_obj.exit_time.tz_convert('America/New_York') if trade_obj.exit_time.tzinfo else trade_obj.exit_time
            trade_detail_str = (
                f"Trade {trade_obj.id}: {trade_obj.symbol} {trade_obj.side} {trade_obj.entry_qty} @ {trade_obj.entry_price} "
                f"(Entry: {display_entry_time}) -> {trade_obj.exit_qty} @ {trade_obj.exit_price} "
                f"(Exit: {display_exit_time}) PnL: {getattr(trade_obj, 'pnl', 'N/A')}"
            )
            flagged_trades_details.append(trade_detail_str)
            # We can also collect other mistakes if needed for these flagged trades
            # other_mistakes = [m for m in trade_obj.mistakes if m != "no stop-loss order"]
            # if other_mistakes:
            #     flagged_trades_details.append(f"  Other mistakes: {other_mistakes}")

    if flagged_trades_details:
        print("\nTrades flagged with 'no stop-loss order' mistake:")
        for detail in flagged_trades_details:
            print(detail)
    else:
        print("\nNo trades were flagged with the 'no stop-loss order' mistake.")

    print(f"\nTotal 'no stop-loss order' mistakes found: {mistake_count} out of {len(analyzed_trades)} trades.")

if __name__ == "__main__":
    main() 