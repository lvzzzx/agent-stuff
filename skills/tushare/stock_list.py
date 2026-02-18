#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tushare>=1.4.0"]
# ///

"""List stocks from Tushare Pro stock_basic interface.

Usage:
    ./stock_list.py                    # All listed stocks
    ./stock_list.py --exchange SSE     # Shanghai only
    ./stock_list.py --exchange SZSE    # Shenzhen only
    ./stock_list.py --market 创业板     # ChiNext only
    ./stock_list.py --hs S             # Shenzhen Connect only
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
    parser = argparse.ArgumentParser(description="List stocks from Tushare")
    parser.add_argument("--exchange", choices=["SSE", "SZSE", "BSE"], help="Filter by exchange")
    parser.add_argument("--market", help="Market type: 主板/创业板/科创板/北交所")
    parser.add_argument("--list-status", choices=["L", "D", "P", "G"], default="L",
                        help="L=Listed, D=Delisted, P=Suspended, G=IPO pending")
    parser.add_argument("--hs", choices=["N", "H", "S"], help="N=None, H=Shanghai Connect, S=Shenzhen Connect")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument("--limit", type=int, help="Limit output to N rows")
    args = parser.parse_args()

    pro = get_pro_api()
    
    kwargs = {
        "list_status": args.list_status,
        "fields": "ts_code,symbol,name,area,industry,market,exchange,list_date,is_hs,act_name"
    }
    
    if args.exchange:
        kwargs["exchange"] = args.exchange
    if args.market:
        kwargs["market"] = args.market
    if args.hs:
        kwargs["is_hs"] = args.hs

    try:
        df = pro.stock_basic(**kwargs)
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("No stocks found matching criteria", file=sys.stderr)
        sys.exit(1)

    if args.limit:
        df = df.head(args.limit)

    if args.csv:
        print(df.to_csv(index=False))
    else:
        # Pretty print
        pd = __import__("pandas")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
                               'display.width', None, 'display.max_colwidth', 20):
            print(df.to_string(index=False))


if __name__ == "__main__":
    main()
