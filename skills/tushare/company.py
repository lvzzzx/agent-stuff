#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["tushare>=1.4.0"]
# ///

"""Get detailed company information.

Usage:
    ./company.py 000001.SZ
    ./company.py 600000.SH
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
    parser = argparse.ArgumentParser(description="Get company information from Tushare")
    parser.add_argument("ts_code", help="Stock code, e.g., 000001.SZ")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    pro = get_pro_api()
    
    try:
        # Get company profile
        company = pro.stock_company(ts_code=args.ts_code)
        
        # Get basic info
        basic = pro.stock_basic(
            ts_code=args.ts_code,
            fields='ts_code,symbol,name,area,industry,fullname,list_date,market,exchange,is_hs,act_name,act_ent_type'
        )
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    if company.empty and basic.empty:
        print(f"No data found for {args.ts_code}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import pandas as pd
        merged = pd.merge(basic, company, on='ts_code', how='outer')
        print(merged.to_json(orient="records", force_ascii=False))
        return

    # Pretty print
    print(f"\n{'='*60}")
    print(f"COMPANY PROFILE: {args.ts_code}")
    print(f"{'='*60}")
    
    if not basic.empty:
        b = basic.iloc[0]
        print(f"\nBasic Information:")
        print(f"  Name (CN):        {b.get('name', 'N/A')}")
        print(f"  Full Name:        {b.get('fullname', 'N/A')}")
        print(f"  Symbol:           {b.get('symbol', 'N/A')}")
        print(f"  Industry:         {b.get('industry', 'N/A')}")
        print(f"  Area:             {b.get('area', 'N/A')}")
        print(f"  Market:           {b.get('market', 'N/A')}")
        print(f"  Exchange:         {b.get('exchange', 'N/A')}")
        print(f"  List Date:        {b.get('list_date', 'N/A')}")
        print(f"  Stock Connect:    {b.get('is_hs', 'N/A')}")
        print(f"  Controller:       {b.get('act_name', 'N/A')}")
        print(f"  Controller Type:  {b.get('act_ent_type', 'N/A')}")
    
    if not company.empty:
        c = company.iloc[0]
        print(f"\nCompany Details:")
        print(f"  English Name:     {c.get('enname', 'N/A')}")
        print(f"  Chairman:         {c.get('chairman', 'N/A')}")
        print(f"  Manager:          {c.get('manager', 'N/A')}")
        print(f"  Secretary:        {c.get('secretary', 'N/A')}")
        print(f"  Reg Capital:      {c.get('reg_capital', 'N/A')}")
        print(f"  Establish Date:   {c.get('setup_date', 'N/A')}")
        print(f"  Province:         {c.get('province', 'N/A')}")
        print(f"  City:             {c.get('city', 'N/A')}")
        print(f"  Employees:        {c.get('employees', 'N/A')}")
        print(f"  Website:          {c.get('website', 'N/A')}")
        print(f"  Email:            {c.get('email', 'N/A')}")
        print(f"  Office:           {c.get('office', 'N/A')}")
        
        if 'main_business' in c and c['main_business']:
            print(f"\nMain Business:")
            print(f"  {c['main_business']}")
        
        if 'introduction' in c and c['introduction']:
            print(f"\nIntroduction:")
            intro = c['introduction']
            if len(intro) > 300:
                intro = intro[:300] + "..."
            print(f"  {intro}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
