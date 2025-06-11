import argparse
from .trade_counter import count_trades

def main() -> None:
    parser = argparse.ArgumentParser(description="Parse and count trades from a NinjaTrader order CSV")
    parser.add_argument("csv", help="Path to the order CSV file")
    parser.add_argument("--verbose", action="store_true", help="Print sample trades")

    args = parser.parse_args()
    trades = count_trades(args.csv)

    print(f"Total trades: {len(trades)}")

    if args.verbose:
        print("\nSample trades:")
        for trade in trades[:5]:
            print(trade)

if __name__ == "__main__":
    main()
