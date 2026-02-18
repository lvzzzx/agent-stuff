---
name: tushare
description: "Access Chinese financial markets data via Tushare Pro. Query A-share stocks (Shanghai/Shenzhen), Beijing stocks, Hong Kong stocks with daily prices, financial statements (income/balance/cashflow), and 200+ financial indicators. Primary key is ts_code (e.g., 000001.SZ). Requires TUSHARE_TOKEN environment variable."
---

# Tushare Pro - Chinese Financial Data

Financial data platform for Chinese markets (A-shares SSE/SZSE, Beijing Exchange BSE, Hong Kong HKEX). Provides stock prices, financial statements, and calculated ratios.

**Setup:**
1. Get token: Register at tushare.pro and copy token from tushare.pro/user/token
2. Set env var: `export TUSHARE_TOKEN="your_token"`

**Running Scripts:** Scripts use `uv` inline metadata. Run with:
```bash
# Using uv run (auto-installs tushare)
uv run --script ./search.py 平安银行

# Or install tushare first
uv add tushare
python ./search.py 平安银行
```

**Rate Limits:** 500 calls/min base; point-based system (free tier: 200 points/day)

---

## STOCK CODE FORMAT

| Exchange | Suffix | Example | Description |
|----------|--------|---------|-------------|
| Shanghai | .SH | 600000.SH | A-shares (6xxxxx), indices (000xxx) |
| Shenzhen | .SZ | 000001.SZ | A-shares (000xxx, 002xxx), indices (399xxx) |
| Beijing | .BJ | 835305.BJ | Beijing Exchange (8xxxxx, 9xxxxx) |
| Hong Kong | .HK | 00001.HK | HKEX stocks |

---

## QUICK REFERENCE - HELPER SCRIPTS

| Script | Purpose | Example (with uv) |
|--------|---------|-------------------|
| `search.py` | Find stocks by name/keyword | `uv run --script ./search.py 平安银行` |
| `stock_list.py` | List all stocks | `uv run --script ./stock_list.py --exchange SSE` |
| `daily_price.py` | Get daily OHLCV prices | `uv run --script ./daily_price.py 000001.SZ --days 30` |
| `financial.py` | Get financial statements | `uv run --script ./financial.py indicators 000001.SZ` |
| `company.py` | Get company profile | `uv run --script ./company.py 000001.SZ` |

---

## 1. STOCK UNIVERSE

### stock_basic - Master Stock List
Primary reference for all listed securities. Cache locally - changes infrequently.

**Input Parameters:**
| Parameter | Required | Values | Description |
|-----------|----------|--------|-------------|
| ts_code | No | 000001.SZ | Specific stock code |
| exchange | No | SSE/SZSE/BSE | Filter by exchange |
| list_status | No | L/D/P/G | L=Listed, D=Delisted, P=Suspended, G=IPO pending |
| market | No | 主板/创业板/科创板/CDR/北交所 | Market segment |
| is_hs | No | N/H/S | N=None, H=Shanghai Connect, S=Shenzhen Connect |

**Output Fields:**
| Field | Type | Description |
|-------|------|-------------|
| ts_code | str | **PRIMARY KEY**. Format: {code}.{exchange} |
| symbol | str | Numeric code without suffix |
| name | str | Chinese short name (e.g., 平安银行) |
| area | str | Province/City (e.g., 深圳, 北京) |
| industry | str | Industry classification (e.g., 银行, 全国地产) |
| fullname | str | Full registered company name |
| enname | str | English name |
| market | str | Market type: 主板, 创业板, 科创板, 北交所, CDR |
| exchange | str | SSE, SZSE, BSE |
| list_status | str | L=Listed, D=Delisted, P=Suspended, G=IPO pending |
| list_date | str | IPO date (YYYYMMDD) |
| delist_date | str | Delisting date (if applicable) |
| is_hs | str | Stock Connect: N=None, H=Shanghai, S=Shenzhen |
| act_name | str | Actual controller name |
| act_ent_type | str | Controller type (地方国企, 民营企业, etc.) |

**Using helper script:**
```bash
# With uv (recommended)
uv run --script ./stock_list.py
uv run --script ./stock_list.py --exchange SSE
uv run --script ./stock_list.py --market 创业板
uv run --script ./stock_list.py --csv > stocks.csv

# Or if tushare is installed globally
./stock_list.py
```

**Python SDK:**
```python
import tushare as ts
pro = ts.pro_api()

# All currently listed stocks
stocks = pro.stock_basic(list_status='L')

# Shanghai stocks only
sse = pro.stock_basic(exchange='SSE', list_status='L')

# Shenzhen Connect eligible
sz_hk = pro.stock_basic(is_hs='S')
```

---

## 2. MARKET DATA

### daily - Daily OHLCV Prices
End-of-day unadjusted prices. Data available after 15:00-16:00 each trading day.

**Input Parameters:**
| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| ts_code | No* | 000001.SZ | Single or multiple (comma-separated) |
| trade_date | No | YYYYMMDD | Specific trading day |
| start_date | No | YYYYMMDD | Date range start |
| end_date | No | YYYYMMDD | Date range end |

*Either ts_code OR trade_date required. Use trade_date alone to get all stocks for one day.

**Output Fields:**
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| ts_code | str | - | Stock identifier |
| trade_date | str | YYYYMMDD | Trading date |
| open | float | CNY | Opening price |
| high | float | CNY | Highest price |
| low | float | CNY | Lowest price |
| close | float | CNY | Closing price |
| pre_close | float | CNY | Previous close (adjusted for splits) |
| change | float | CNY | Price change amount |
| pct_chg | float | % | Percentage change |
| vol | float | 手 | Trading volume (1 手 = 100 shares) |
| amount | float | 千元 | Trading value (1000 CNY) |

**Using helper script:**
```bash
# With uv (recommended)
uv run --script ./daily_price.py 000001.SZ --start 20240101 --end 20241231
uv run --script ./daily_price.py 000001.SZ --days 30 --csv

# Or if tushare is installed globally
./daily_price.py 000001.SZ --start 20240101 --end 20241231
```

**Python SDK:**
```python
# Single stock history
pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20241231')

# Multiple stocks
pro.daily(ts_code='000001.SZ,600000.SH', start_date='20240101')

# Single day all stocks (heavy query)
pro.daily(trade_date='20241201')

# Recent 30 days
pro.daily(ts_code='000001.SZ', start_date='20241101', end_date='20241201')
```

### adj_factor - Price Adjustment Factors
Cumulative adjustment factors for stock splits, dividends, rights issues.

**Output Fields:**
| Field | Description |
|-------|-------------|
| ts_code | Stock code |
| trade_date | Date |
| adj_factor | Cumulative adjustment factor |

**Adjusted Price Calculation:**
```python
# Get prices and adjustment factors
prices = pro.daily(ts_code='000001.SZ', start_date='20200101', end_date='20241201')
factors = pro.adj_factor(ts_code='000001.SZ')

# Merge and calculate adjusted close
df = prices.merge(factors[['trade_date', 'adj_factor']], on='trade_date')
latest_factor = df['adj_factor'].iloc[-1]
df['adj_close'] = df['close'] * df['adj_factor'] / latest_factor
```

### daily_basic - Daily Market Metrics
Daily valuation multiples and trading statistics.

**Key Fields:**
| Field | Description |
|-------|-------------|
| turnover_rate | Turnover ratio (%) |
| turnover_rate_f | Free-float turnover (%) |
| volume_ratio | Volume ratio vs. recent average |
| pe | P/E ratio (TTM) |
| pe_ttm | P/E ratio TTM |
| pb | P/B ratio |
| ps | P/S ratio |
| ps_ttm | P/S ratio TTM |
| dv_ratio | Dividend yield (%) |
| total_share | Total shares outstanding |
| float_share | Free-float shares |
| total_mv | Total market cap (10k CNY) |
| circ_mv | Float market cap (10k CNY) |

---

## 3. FINANCIAL STATEMENTS

Quarterly and annual statements. Report periods end on: 0331, 0630, 0930, 1231.

### income - Income Statement (利润表)

**Key Fields:**
| Field | Chinese | Description |
|-------|---------|-------------|
| total_revenue | 营业总收入 | Total operating revenue |
| revenue | 营业收入 | Main business revenue |
| total_cogs | 营业总成本 | Total cost of goods sold |
| oper_cost | 营业成本 | Operating cost |
| operating_expense | 营业费用 | Operating expenses (legacy) |
| admin_expense | 管理费用 | Administrative expenses |
| selling_expense | 销售费用 | Selling expenses |
| financial_expense | 财务费用 | Financial/interest expenses |
| operate_profit | 营业利润 | Operating profit |
| total_profit | 利润总额 | Total profit before tax |
| n_income | 净利润 | Net income (consolidated) |
| n_income_attr_p | 归属于母公司股东的净利润 | **Most important**: Net profit attributable to parent company |
| basic_eps | 基本每股收益 | Basic EPS |
| diluted_eps | 稀释每股收益 | Diluted EPS |
| other_income | 其他收益 | Other operating income |
| invest_income | 投资收益 | Investment income |
| f_value_chg_income | 公允价值变动收益 | Fair value change income |

**Example:**
```python
pro.income(ts_code='600000.SH', start_date='20200101', end_date='20241231')

# Specific quarter
pro.income(ts_code='600000.SH', period='20240930')
```

### balance_sheet - Balance Sheet (资产负债表)

**Key Fields:**
| Field | Description |
|-------|-------------|
| total_assets | Total assets |
| total_liab | Total liabilities |
| total_hldr_eqy_exc_min_int | Total equity excl. minority interest |
| total_hldr_eqy_inc_min_int | Total equity incl. minority interest |
| money_cap | Cash and cash equivalents |
| trad_asset | Trading financial assets |
| accounts_receiv | Accounts receivable |
| inventories | Inventory |
| fix_assets | Fixed assets (net) |
| total_curr_assets | Total current assets |
| total_non_curr_assets | Total non-current assets |
| total_curr_liab | Total current liabilities |
| total_non_curr_liab | Total non-current liabilities |
| notes_receiv | Notes receivable |
| prepayment | Prepayments |
| intan_assets | Intangible assets |
| goodwill | Goodwill |

### cashflow - Cash Flow Statement (现金流量表)

**Key Fields:**
| Field | Description |
|-------|-------------|
| n_cashflow_act | Net cash from operating activities |
| c_inf_fr_operate_a | Cash inflow from operations |
| c_paid_for_goods_a | Cash paid for goods/services |
| n_cashflow_inv_act | Net cash from investing activities |
| c_pay_acq_const_fiolta | Cash paid for fixed assets |
| n_cash_flows_fnc_act | Net cash from financing activities |
| c_pay_dist_dpcp_int_exp | Cash paid for dividends/interest |
| im_net_cashflow_oper_act | Indirect method operating cash flow |

---

## 4. FINANCIAL INDICATORS

### fina_indicator - Calculated Financial Ratios (财务指标)
200+ pre-calculated metrics. Most comprehensive fundamental data source.
Requires 2000+ points. Use `fina_indicator_vip` for bulk queries (5000+ points).

**Profitability Ratios:**
| Field | Description |
|-------|-------------|
| eps | Basic earnings per share |
| dt_eps | Diluted EPS |
| bps | Book value per share |
| roe | Return on equity (%) |
| roe_waa | Weighted average ROE (%) |
| roe_dt | ROE excluding extraordinary items (%) |
| roa | Return on assets (%) |
| roic | Return on invested capital (%) |
| grossprofit_margin | Gross profit margin (%) |
| netprofit_margin | Net profit margin (%) |

**Per Share Metrics:**
| Field | Description |
|-------|-------------|
| ocfps | Operating cash flow per share |
| cfps | Cash flow per share |
| fcff_ps | Free cash flow to firm per share |
| fcfe_ps | Free cash flow to equity per share |
| revenue_ps | Revenue per share |
| capital_rese_ps | Capital reserve per share |
| surplus_rese_ps | Surplus reserve per share |
| undist_profit_ps | Undistributed profit per share |

**Leverage & Solvency:**
| Field | Description |
|-------|-------------|
| debt_to_assets | Debt-to-assets ratio (%) |
| current_ratio | Current ratio (current assets/current liabilities) |
| quick_ratio | Quick ratio (excluding inventory) |
| cash_ratio | Cash ratio (cash/current liabilities) |
| debt_to_eqt | Debt-to-equity ratio |
| eqt_to_debt | Equity-to-debt ratio |
| tangibleasset_to_debt | Tangible assets to debt |

**Efficiency Ratios:**
| Field | Description |
|-------|-------------|
| assets_turn | Total asset turnover |
| inv_turn | Inventory turnover |
| ar_turn | Accounts receivable turnover |
| invturn_days | Inventory turnover days |
| arturn_days | AR turnover days |
| turn_days | Operating cycle days |

**Growth Rates (Year-over-Year %):**
| Field | Description |
|-------|-------------|
| basic_eps_yoy | EPS growth YoY |
| netprofit_yoy | Net profit growth YoY |
| dt_netprofit_yoy | Net profit growth YoY (adjusted) |
| tr_yoy | Total revenue growth YoY |
| or_yoy | Operating revenue growth YoY |
| ocf_yoy | Operating cash flow growth YoY |
| bps_yoy | Book value per share growth YoY |
| roe_yoy | ROE growth YoY |

**Quarterly Fields (prefix q_):**
Single quarter values (vs. cumulative YTD for quarterly reports before Q4):
| Field | Description |
|-------|-------------|
| q_sales_yoy | Quarterly revenue growth YoY |
| q_sales_qoq | Quarterly revenue growth QoQ |
| q_op_yoy | Quarterly operating profit growth YoY |
| q_op_qoq | Quarterly operating profit growth QoQ |
| q_roe | Quarterly ROE |
| q_dt_roe | Quarterly ROE (adjusted) |
| q_npta | Quarterly net profit to total assets |
| q_ocf_to_sales | Quarterly OCF to sales |

**Using helper script:**
```bash
# With uv (recommended)
uv run --script ./financial.py indicators 000001.SZ --period 20240930
uv run --script ./financial.py indicators 000001.SZ --start 20200101 --end 20241231 --csv
uv run --script ./financial.py all 000001.SZ       # All statement types (latest)

# Or if tushare is installed globally
./financial.py indicators 000001.SZ --period 20240930
```

**Python SDK:**
```python
# All historical indicators for a stock
pro.fina_indicator(ts_code='600000.SH')

# Date range
pro.fina_indicator(ts_code='600000.SH', start_date='20200101', end_date='20241231')

# Specific quarter
pro.fina_indicator(ts_code='600000.SH', period='20240930')
```

---

## 5. COMPANY INFORMATION

### stock_company - Company Profile (上市公司基本信息)

**Output Fields:**
| Field | Description |
|-------|-------------|
| ts_code | Stock code |
| exchange | Exchange |
| full_name | Full registered company name |
| en_name | English name |
| actual_controller | Actual controller |
| chairman | Chairman name |
| manager | General manager/CEO |
| secretary | Board secretary |
| reg_capital | Registered capital |
| setup_date | Company establishment date |
| province | Province |
| city | City |
| introduction | Business description |
| website | Company website |
| email | Contact email |
| office | Office address |
| employees | Employee count |
| main_business | Main business segments |
| business_scope | Full business scope |

**Using helper script:**
```bash
# With uv (recommended)
uv run --script ./company.py 000001.SZ
uv run --script ./search.py 平安银行              # Search by name
uv run --script ./search.py 银行                  # Search by industry

# Or if tushare is installed globally
./company.py 000001.SZ
```

---

## DATA RELATIONSHIPS

```
stock_basic (master stock list)
    │
    ├── daily (daily prices) ←── adj_factor (adjustments)
    │
    ├── daily_basic (market metrics)
    │
    ├── income (quarterly/annual income statement)
    │
    ├── balance_sheet (quarterly/annual balance sheet)
    │
    ├── cashflow (quarterly/annual cash flow)
    │
    ├── fina_indicator (calculated financial ratios)
    │
    └── stock_company (company profile)
```

**Join Keys:**
- Primary: `ts_code` (000001.SZ format)
- Date: `trade_date` (daily), `end_date` (financial), `ann_date` (announcement)

---

## COMMON QUERY PATTERNS

### Complete fundamental snapshot
```python
import tushare as ts
import pandas as pd

pro = ts.pro_api()
ts_code = '000001.SZ'

# 1. Latest financial indicators
indicators = pro.fina_indicator(ts_code=ts_code, period='20240930')

# 2. Company profile
company = pro.stock_company(ts_code=ts_code)

# 3. Current price
price = pro.daily(ts_code=ts_code, trade_date='20241201')

# 4. Recent price history
history = pro.daily(ts_code=ts_code, start_date='20241101', end_date='20241201')
```

### Stock screening by financial criteria
```python
# Get stock universe
stocks = pro.stock_basic(list_status='L', fields='ts_code,name,industry')

# Filter by industry
banks = stocks[stocks['industry'] == '银行']

# Get metrics for each
results = []
for code in banks['ts_code'][:10]:
    fina = pro.fina_indicator(ts_code=code, period='20240930')
    if not fina.empty:
        results.append(fina.iloc[0])

metrics = pd.DataFrame(results)
# Now filter by ROE, debt ratios, etc.
```

### Time series analysis
```python
# 5-year daily prices
prices = pro.daily(ts_code='000001.SZ', 
                   start_date='20200101', 
                   end_date='20241231')

# Quarterly financials
financials = pro.fina_indicator(ts_code='000001.SZ',
                                start_date='20200101',
                                end_date='20241231')

# Merge prices with financials on nearest date
# (financials released quarterly, prices daily)
```

---

## CHINESE FINANCIAL TERMS

**Key Terms in Data Fields:**
| Chinese | English | Common Fields |
|---------|---------|---------------|
| 营业总收入 | Total operating revenue | total_revenue |
| 营业收入 | Operating revenue | revenue |
| 营业成本 | Operating cost | oper_cost |
| 营业利润 | Operating profit | operate_profit |
| 利润总额 | Total profit | total_profit |
| 净利润 | Net income | n_income |
| 归属于母公司股东的净利润 | Net profit attributable to parent | **n_income_attr_p** |
| 基本每股收益 | Basic EPS | basic_eps |
| 扣除非经常性损益 | Excluding extraordinary items | _dt suffix |
| 同比 | Year-over-year | _yoy suffix |
| 环比 | Quarter-over-quarter | _qoq suffix |
| 总资产 | Total assets | total_assets |
| 总负债 | Total liabilities | total_liab |
| 股东权益 | Shareholders' equity | total_hldr_eqy_exc_min_int |
| 经营活动现金流 | Operating cash flow | n_cashflow_act |
| 净资产收益率 | Return on equity | roe |
| 市盈率 | P/E ratio | pe, pe_ttm |
| 市净率 | P/B ratio | pb |

---

## POINTS & ACCESS LEVELS

| Interface | Min Points | Notes |
|-----------|------------|-------|
| stock_basic | 200 | One-time cache recommended |
| daily | 200 | 500 calls/min, 6000 rows/call |
| daily_basic | 200 | Daily market metrics |
| income | 2000 | Quarterly/annual statements |
| balance_sheet | 2000 | |
| cashflow | 2000 | |
| fina_indicator | 2000 | 200+ calculated ratios |
| fina_indicator_vip | 5000 | Bulk quarter data (all stocks) |

---

## TIPS

1. **Cache stock_basic**: Download once, save locally. Changes infrequently.

2. **Use ts_code format**: Always include exchange suffix (.SH/.SZ/.BJ/.HK)

3. **Financial report timing**: Quarterly reports released 1-2 months after quarter end. Check `ann_date` field.

4. **n_income_attr_p vs n_income**: Use `n_income_attr_p` for parent company profit (most relevant for stock analysis).

5. **Adjusted prices**: Use `adj_factor` for split/dividend adjusted prices.

6. **Q4 = Annual**: Annual reports (1231 period) contain full year data, not just Q4.

7. **Growth rates**: Fields ending in `_yoy` are already calculated YoY percentages.
