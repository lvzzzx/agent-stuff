#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tushare>=1.4.0"]
# ///

"""Fetch daily OHLCV price data from Tushare.

Usage:
    ./daily_price.py 000001.SZ --start 20240101 --end 20241231
    ./daily_price.py 000001.SZ --days 30
    ./daily_price.py 600000.SH --trade-date 20241201
    ./daily_price.py "000001.SZ,600000.SH" --start 20240101 --csv
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

import tushare as ts


def get_pro_api():
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        print("Error: TUSHARE_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    return ts.pro_api(token)


def main():
    parser = argparse.ArgumentParser(description="Fetch daily stock prices from Tushare")
    parser.add_argument("ts_code", help="Stock code(s), e.g., 000001.SZ or comma-separated")
    parser.add_argument("--start", help="Start date (YYYYMMDD)")
    parser.add_argument("--end", help="End date (YYYYMMDD)")
    parser.add_argument("--days", type=int, help="Fetch last N trading days")
    parser.add_argument("--trade-date", help="Single trading date (YYYYMMDD)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    pro = get_pro_api()
    
    kwargs = {}
    
    # Handle date range vs single date
    if args.trade_date:
        kwargs["trade_date"] = args.trade_date
    else:
        if args.days and not args.start:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=args.days * 2)  # Approximate trading days
            kwargs["start_date"] = start_date.strftime("%Y%m%d")
            kwargs["end_date"] = end_date.strftime("%Y%m%d")
        else:
            if not args.start:
                # Default to 30 days ago
                end_date = datetime.now()
                start_date = end_date - timedelta(days=60)
                kwargs["start_date"] = start_date.strftime("%Y%m%d")
                kwargs["end_date"] = end_date.strftime("%Y%m%d")
            else:
                kwargs["start_date"] = args.start
                kwargs["end_date"] = args.end or datetime.now().strftime("%Y%m%d")
        
        kwargs["ts_code"] = args.ts_code

    try:
        df = pro.daily(**kwargs)
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("No data found", file=sys.stderr)
        sys.exit(1)

    # Sort by date
    df = df.sort_values("trade_date")

    if args.csv:
        print(df.to_csv(index=False))
    elif args.json:
        print(df.to_json(orient="records", force_ascii=False))
    else:
        pd = __import__("pandas")
        with pd.option_context('display.max_rows', None, 'display.width', None):
            print(df.to_string(index=False))


if __name__ == "__main__":
    main()
