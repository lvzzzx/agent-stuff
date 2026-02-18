---
name: quant360
description: >-
  Quant360 Chinese stock Level 2/3 data format and Chinese A-share trading rules
  reference. Use when: (1) parsing or writing parsers for Quant360 order/tick/L2
  CSV files, (2) working with SSE or SZSE exchange feed schemas and their differences,
  (3) determining aggressor side from order references, (4) understanding Chinese
  stock trading phases, auction mechanisms, or price limit rules, (5) working with
  CN L2/L3 market microstructure data.
---

# Quant360 — Chinese Stock Level 2/3 Data

Quant360 (data.quant360.com) provides Level 2/3 tick-by-tick data for Chinese A-shares: order streams, trade/tick streams, and L2 order book snapshots for SSE and SZSE.

## Data Format

- **Delivery:** `.7z` archives (LZMA2), one per type/exchange/date
- **Internal:** One CSV per symbol (e.g., `600000.csv`, `000001.csv`)
- **Encoding:** UTF-8, header row
- **Timestamps:** `YYYYMMDDHHMMSSmmm` format, China Standard Time (UTC+8)

### File Naming

```
<type>_<market>_<exchange>_<YYYYMMDD>.7z
```

| Component | Values |
|---|---|
| `type` | `order_new`, `tick_new`, `L2_new` |
| `market` | `STK` (stocks), `ConFI` (convertible bonds) |
| `exchange` | `SH` (SSE), `SZ` (SZSE) |

## SSE vs SZSE — Key Differences

| Feature | SSE (SH) | SZSE (SZ) |
|---|---|---|
| Symbol location | `SecurityID` column | Filename only |
| Order ID | `OrderNo` | `ApplSeqNum` |
| Side encoding | `B`/`S` (strings) | `1`/`2` (integers) |
| Order type | `A`=Add, `D`=Delete | `1`=Market, `2`=Limit |
| Cancel events | `OrdType='D'` in order stream | `ExecType='4'` in tick stream |
| Trade linkage | `BuyNo` + `SellNo` | `BidApplSeqNum` + `OfferApplSeqNum` |
| Trade direction | Explicit `TradeBSFlag` (B/S/N) | Inferred from order refs |
| L2 snapshots | Available (`L2_new_*`) | Available (`L2_new_*`) |
| Closing auction | No explicit phase (14:57-15:00 is closed) | Dedicated 14:57-15:00 phase |

## Schema Comparison: Tick/Trade Stream

**⚠️ Critical: SSE and SZSE have completely different column schemas. You cannot use the same parser for both.**

| Column Concept | SSE (SH) | SZSE (SZ) | Notes |
|---|---|---|---|
| **Symbol** | `SecurityID` | *Filename only* | SZSE: Extract from CSV filename |
| **Event ID** | `TradeIndex` | `ApplSeqNum` | Different sequence spaces |
| **Timestamp** | `TradeTime` | `SendingTime` + `TransactTime` | SZSE has gateway + exchange times |
| **Price** | `TradePrice` | `Price` | Different column names |
| **Quantity** | `TradeQty` | `Qty` | Different column names |
| **Notional** | `TradeAmount` | `Amt` | Different column names |
| **Buy Order Ref** | `BuyNo` | `BidApplSeqNum` | Links to order file |
| **Sell Order Ref** | `SellNo` | `OfferApplSeqNum` | Links to order file |
| **Aggressor Flag** | `TradeBSFlag` (B/S/N) | *Not present* | SZSE: Infer from order refs |
| **Event Type** | *Implicit* | `ExecType` (F/4) | SZSE: 'F'=Fill, '4'=Cancel |
| **Channel** | `ChannelNo` | `ChannelNo` | ✅ Same name |
| **Global Index** | `BizIndex` | *Not present* | SSE only |

**Key Takeaway:** SZSE has 10 columns, SSE has 11 columns. Column names are completely different except for `ChannelNo`. SZSE requires order reference comparison to determine aggressor side; SSE provides it explicitly.

## Aggressor Side Determination

Compare order reference numbers — the later-arriving (higher sequence) order is the aggressor:

```
BuyOrderRef > SellOrderRef → BUYER is aggressor (主动买 / 外盘)
SellOrderRef > BuyOrderRef → SELLER is aggressor (主动卖 / 内盘)
```

- SSE provides `TradeBSFlag` directly but can be cross-validated with order refs
- SZSE has no native flag — must infer from `BidApplSeqNum` vs `OfferApplSeqNum`
- Auction trades (`TradeBSFlag='N'` or equal refs) → `UNKNOWN`

## Chinese A-Share Trading Rules

### Trading Sessions (CST / UTC+8)

| Phase | Time | Description |
|---|---|---|
| Pre-Open Auction | 09:15 - 09:25 | Call auction, orders accepted |
| Opening Auction | 09:25 - 09:30 | Opening price determination |
| Morning Session | 09:30 - 11:30 | Continuous trading |
| Lunch Break | 11:30 - 13:00 | No trading |
| Afternoon Session | 13:00 - 14:57 | Continuous trading |
| Closing Auction (SZSE only) | 14:57 - 15:00 | Closing price determination |
| After-Hours (STAR/ChiNext only) | 15:05 - 15:30 | Limited trading |

### Price Limits (涨跌停)

| Board | Daily Limit | Notes |
|---|---|---|
| Main Board (主板) | ±10% | Based on previous close |
| ChiNext (创业板) | ±20% | Since 2020 reform |
| STAR Market (科创板) | ±20% | Since inception |
| New listings | No limit for first 5 days | ChiNext/STAR Market only |

### Order Types

| Type | Description |
|---|---|
| Limit Order | Trade at specified price or better |
| Market Order | Trade immediately at best available price |
| Cancel | Withdraw a resting order from the book |

### Lot Sizes

| Board | Standard Lot |
|---|---|
| Main Board / ChiNext | 100 shares |
| STAR Market (科创板) | 200 shares |

### Tick Size

All boards: **0.01 CNY** per share.

## Quick Schema Reference

### Order Stream — SSE

`SecurityID`, `TransactTime`, `OrderNo`, `Price`, `Balance`, `OrderBSFlag` (B/S), `OrdType` (A/D), `OrderIndex`, `ChannelNo`, `BizIndex`

### Order Stream — SZSE

`ApplSeqNum`, `Side` (1/2), `OrdType` (1/2), `Price`, `OrderQty`, `TransactTime`, `ChannelNo`
(Symbol from filename; also includes optional `ExpirationDays`, `ExpirationType`, `Contactor`, `ConfirmID`)

### Tick/Trade Stream — SSE

`SecurityID`, `TradeTime`, `TradePrice`, `TradeQty`, `TradeAmount`, `BuyNo`, `SellNo`, `TradeIndex`, `ChannelNo`, `TradeBSFlag` (B/S/N), `BizIndex`

### Tick/Trade Stream — SZSE

`ApplSeqNum`, `BidApplSeqNum`, `SendingTime`, `Price`, `ChannelNo`, `Qty`, `OfferApplSeqNum`, `Amt`, `ExecType`, `TransactTime`

**Important:** 
- Symbol from filename (no `SecurityID` column)
- `ExecType='F'`=Fill (trade), `'4'`=Cancel (withdrawal)
- Early morning data (09:15-09:30) contains mostly cancel events (`ExecType='4'`) as orders are rejected or withdrawn during auction phases

### L2 Snapshots — SSE & SZSE

Available for both exchanges via `L2_new_STK_SH_*.7z` and `L2_new_STK_SZ_*.7z`.

**⚠️ SSE and SZSE L2 snapshots have different column schemas. You cannot use the same parser for both.**

~3-second snapshot intervals during trading hours. Array fields use JSON bracket notation: `"[11.63,11.62,11.61,...]"`

#### L2 Schema Comparison

| Column Concept | SSE (SH) | SZSE (SZ) | Notes |
|---|---|---|---|
| **Symbol** | `SecurityID` | *Filename only* | Same pattern as tick/order streams |
| **Timestamp** | `DateTime` | `QuotTime` + `SendingTime` | SZSE has gateway + exchange times |
| **Volume** | `TotalVolumeTrade` | `Volume` | Different column names |
| **Amount** | `TotalValueTrade` | `Amount` | Different column names |
| **Trading Phase** | `InstrumentStatus` | `TradingPhaseCode` | Different encoding (see below) |
| **Bid/Offer NumOrders** | **Array[10]** (per-level) | **Scalar** (total) | Critical difference |
| **Close Price** | *Not present* | `ClosePx` | SZSE only |
| **Average Price** | *Not present* | `AveragePx` | SZSE only |
| **Price Limits** | *Not present* | `UpperLimitPx`, `LowerLimitPx` | SZSE only |
| **PE Ratios** | *Not present* | `PeRatio1`, `PeRatio2` | SZSE only |
| **IOPV** | `IOPV` | *Not present* | SSE only (ETF indicator value) |
| **Withdraw stats** | `WithdrawBuy/Sell*` (6 cols) | *Not present* | SSE only |
| **ETF stats** | `ETFBuy/Sell*` (6 cols) | *Not present* | SSE only |
| **Order count stats** | `NumBidOrders`, `NumOfferOrders`, `TotalBidNumber`, `TotalOfferNumber` | `NoOrdersB1`, `NoOrdersS1` | SSE has 4 fields, SZSE has 2 |
| **Max duration** | `BidTradeMaxDuration`, `OfferTradeMaxDuration` | *Not present* | SSE only |
| **Sequence** | *Not present* | `MsgSeqNum` | SZSE only |
| **Image flag** | *Not present* | `ImageStatus` | SZSE only |

#### Trading Phase Encoding

| Phase | SSE `InstrumentStatus` | SZSE `TradingPhaseCode` |
|---|---|---|
| Pre-open / Opening Call | `OCALL` | `S0` (Start) |
| Opening price determination | `OCALL` | `O0` (Open) |
| Continuous Trading | `TRADE` | `T0` (Trade) |
| Lunch Break | `TRADE` → `OCALL` | `B0` (Break) |
| Closing Call (14:57-15:00) | `CCALL` | `C0` (Close) |
| Market Closed | `CLOSE` | `E0` (End) |
| End of Transmission | `ENDTR` | `E0` |

#### L2 Snapshot — SSE (42 columns)

`SecurityID`, `DateTime`, `PreClosePx`, `OpenPx`, `HighPx`, `LowPx`, `LastPx`, `TotalVolumeTrade`, `TotalValueTrade`, `InstrumentStatus`, `BidPrice` (10 levels), `BidOrderQty` (10 levels), `BidNumOrders` **(10 levels array)**, `BidOrders` (50 entries), `OfferPrice` (10 levels), `OfferOrderQty` (10 levels), `OfferNumOrders` **(10 levels array)**, `OfferOrders` (50 entries), `NumTrades`, `IOPV`, `TotalBidQty`, `TotalOfferQty`, `WeightedAvgBidPx`, `WeightedAvgOfferPx`, `TotalBidNumber`, `TotalOfferNumber`, `BidTradeMaxDuration`, `OfferTradeMaxDuration`, `NumBidOrders`, `NumOfferOrders`, `WithdrawBuyNumber`, `WithdrawBuyAmount`, `WithdrawBuyMoney`, `WithdrawSellNumber`, `WithdrawSellAmount`, `WithdrawSellMoney`, `ETFBuyNumber`, `ETFBuyAmount`, `ETFBuyMoney`, `ETFSellNumber`, `ETFSellAmount`, `ETFSellMoney`

#### L2 Snapshot — SZSE (38 columns)

`SendingTime`, `MsgSeqNum`, `ImageStatus`, `QuotTime`, `PreClosePx`, `OpenPx`, `HighPx`, `LowPx`, `LastPx`, `ClosePx`, `Volume`, `Amount`, `AveragePx`, `BidPrice` (10 levels), `BidOrderQty` (10 levels), `BidNumOrders` **(scalar)**, `BidOrders` (50 entries), `OfferPrice` (10 levels), `OfferOrderQty` (10 levels), `OfferNumOrders` **(scalar)**, `OfferOrders` (50 entries), `NumTrades`, `TotalBidQty`, `WeightedAvgBidPx`, `TotalOfferQty`, `WeightedAvgOfferPx`, `Change1`, `Change2`, `TotalLongPosition`, `PeRatio1`, `PeRatio2`, `UpperLimitPx`, `LowerLimitPx`, `WeightedAvgPxChg`, `PreWeightedAvgPx`, `TradingPhaseCode`, `NoOrdersB1`, `NoOrdersS1`

## Symbol Code Ranges

| Exchange | Code Range | Market |
|---|---|---|
| SSE | 600000-699999 | Main Board |
| SSE | 680000-689999 | STAR Market (科创板) |
| SSE | 510000-519999 | ETFs |
| SZSE | 000001-009999 | Main Board |
| SZSE | 300000-309999 | ChiNext (创业板) |
| SZSE | 159000-159999 | ETFs |

## Full Data Format Reference

For complete column definitions, exchange semantics, timestamp details, and data volume estimates, read [references/quant360_cn_l2.md](references/quant360_cn_l2.md).
