#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tushare>=1.4.0"]
# ///

"""Fetch financial data from Tushare.

Usage:
    # Financial indicators (200+ ratios)
    ./financial.py indicators 000001.SZ --period 20240930
    ./financial.py indicators 000001.SZ --start 20200101 --end 20241231
    
    # Income statement
    ./financial.py income 000001.SZ --period 20240930
    
    # Balance sheet
    ./financial.py balance 000001.SZ --period 20240930
    
    # Cash flow
    ./financial.py cashflow 000001.SZ --period 20240930
    
    # Latest quarter for all statement types
    ./financial.py all 000001.SZ
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
    parser = argparse.ArgumentParser(description="Fetch financial data from Tushare")
    parser.add_argument("type", choices=["indicators", "income", "balance", "cashflow", "all"],
                        help="Type of financial data to fetch")
    parser.add_argument("ts_code", help="Stock code, e.g., 000001.SZ")
    parser.add_argument("--period", help="Report period (YYYYMMDD), e.g., 20240930 for Q3 2024")
    parser.add_argument("--start", help="Start date (YYYYMMDD)")
    parser.add_argument("--end", help="End date (YYYYMMDD)")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fields", help="Comma-separated field list (for indicators)")
    args = parser.parse_args()

    pro = get_pro_api()
    
    kwargs = {"ts_code": args.ts_code}
    
    if args.period:
        kwargs["period"] = args.period
    if args.start:
        kwargs["start_date"] = args.start
    if args.end:
        kwargs["end_date"] = args.end

    try:
        if args.type == "indicators":
            if args.fields:
                kwargs["fields"] = args.fields
            df = pro.fina_indicator(**kwargs)
        elif args.type == "income":
            df = pro.income(**kwargs)
        elif args.type == "balance":
            df = pro.balance_sheet(**kwargs)
        elif args.type == "cashflow":
            df = pro.cashflow(**kwargs)
        elif args.type == "all":
            # Fetch latest of each type
            income_df = pro.income(ts_code=args.ts_code, limit=1)
            balance_df = pro.balance_sheet(ts_code=args.ts_code, limit=1)
            cashflow_df = pro.cashflow(ts_code=args.ts_code, limit=1)
            indicator_df = pro.fina_indicator(ts_code=args.ts_code, limit=1)
            
            print("=== INCOME STATEMENT ===")
            print(income_df.to_string(index=False) if not income_df.empty else "No data")
            print("\n=== BALANCE SHEET ===")
            print(balance_df.to_string(index=False) if not balance_df.empty else "No data")
            print("\n=== CASH FLOW ===")
            print(cashflow_df.to_string(index=False) if not cashflow_df.empty else "No data")
            print("\n=== KEY INDICATORS ===")
            if not indicator_df.empty:
                # Show key fields
                key_fields = [
                    'ts_code', 'end_date', 'eps', 'roe', 'roa', 'grossprofit_margin',
                    'netprofit_margin', 'debt_to_assets', 'current_ratio'
                ]
                available_fields = [f for f in key_fields if f in indicator_df.columns]
                print(indicator_df[available_fields].to_string(index=False))
            else:
                print("No data")
            return
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("No data found", file=sys.stderr)
        sys.exit(1)

    # Sort by period date
    if "end_date" in df.columns:
        df = df.sort_values("end_date")
    elif "ann_date" in df.columns:
        df = df.sort_values("ann_date")

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
