#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tushare>=1.4.0"]
# ///

"""Search stocks by name or keyword.

Usage:
    ./search.py 平安银行
    ./search.py 银行
    ./search.py 深圳
    ./search.py 600000  # Search by symbol
"""

import argparse
import os
import sys

import tushare as ts


def get_pro_api():
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        print("Error: TUSHARE_TOKEN environment variable not set", file=sys.stderr)
        print("Get your token from https://tushare.pro/user/token", file=sys.stderr)
        sys.exit(1)
    return ts.pro_api(token)


def main():
    parser = argparse.ArgumentParser(description="Search stocks by name/keyword")
    parser.add_argument("keyword", help="Search keyword (Chinese or symbol)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    args = parser.parse_args()

    pro = get_pro_api()
    
    try:
        # Get all stocks and filter locally
        df = pro.stock_basic(
            list_status='L',
            fields='ts_code,symbol,name,area,industry,market,exchange,list_date,fullname'
        )
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("No stocks found", file=sys.stderr)
        sys.exit(1)

    # Search across multiple fields
    keyword = args.keyword.lower()
    mask = (
        df['name'].str.lower().str.contains(keyword, na=False) |
        df['ts_code'].str.lower().str.contains(keyword, na=False) |
        df['symbol'].str.lower().str.contains(keyword, na=False) |
        df['fullname'].str.lower().str.contains(keyword, na=False) |
        df['industry'].str.contains(keyword, na=False) |
        df['area'].str.contains(keyword, na=False)
    )
    
    results = df[mask]
    
    if results.empty:
        print(f"No stocks found matching '{args.keyword}'", file=sys.stderr)
        sys.exit(1)
    
    results = results.head(args.limit)

    if args.csv:
        print(results.to_csv(index=False))
    else:
        pd = __import__("pandas")
        with pd.option_context('display.max_rows', None, 'display.width', None, 
                               'display.max_colwidth', 25):
            print(results.to_string(index=False))
        print(f"\nFound {len(results)} result(s) (showing first {min(len(results), args.limit)})")


if __name__ == "__main__":
    main()
