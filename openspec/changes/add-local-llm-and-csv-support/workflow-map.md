# Offline/Intranet `main.py` Workflow Map

This document is a quick-reference map of:

- which graph nodes execute when running `main.py`
- which data tools each node can call
- how each tool routes to vendors
- which local files/datasets are required for a strict offline run

The intent is to make local data preparation deterministic and verifiable.

## 1. Graph execution order (default)

`TradingAgentsGraph` defaults to `selected_analysts=["market","social","news","fundamentals"]`.

Execution flow:

1. **Market Analyst**
2. **Social Media Analyst**
3. **News Analyst**
4. **Fundamentals Analyst**
5. **Bull Researcher** ↔ **Bear Researcher** (debate loop)
6. **Research Manager**
7. **Trader**
8. **Risky Analyst** → **Safe Analyst** → **Neutral Analyst** (risk loop)
9. **Risk Judge** → END

Notes:

- Each analyst node can loop `Analyst → tools_* → Analyst` until no tool calls remain.
- After END, `SignalProcessor` calls the LLM to extract BUY/SELL/HOLD (no data tools).

## 2. Tool inventory by node

Tool nodes are wired in `TradingAgentsGraph._create_tool_nodes()`.

### Market Analyst tools

- `get_stock_data(symbol, start_date, end_date)`
- `get_indicators(symbol, indicator, curr_date, look_back_days=30)`

### Social Media Analyst tools

- `get_news(ticker, start_date, end_date)`

### News Analyst tools

- `get_news(ticker, start_date, end_date)`
- `get_global_news(curr_date, look_back_days=7, limit=5)` (disabled in the offline smoke-test profile)
- `get_insider_sentiment(ticker, curr_date)`
- `get_insider_transactions(ticker, curr_date)`

### Fundamentals Analyst tools

- `get_fundamentals(ticker, curr_date)`
- `get_balance_sheet(ticker, freq="quarterly", curr_date)`
- `get_cashflow(ticker, freq="quarterly", curr_date)`
- `get_income_statement(ticker, freq="quarterly", curr_date)`

### Memory (non-tool but required offline)

Bull/Bear/Manager/Trader/Risk Judge call `memory.get_memories(...)` which calls OpenAI-compatible `/embeddings`.

## 3. Tool routing: method → vendor implementations

All tool functions call `route_to_vendor(<method>, ...)` which selects a vendor based on:

- tool-level override: `config["tool_vendors"][method]`
- otherwise category-level: `config["data_vendors"][category]`

Vendors per method (from `tradingagents/dataflows/interface.py`):

- `get_stock_data`: `local`, `yfinance`, `alpha_vantage`
- `get_indicators`: `local`, `yfinance`, `alpha_vantage`
- `get_balance_sheet`: `local`, `yfinance`, `alpha_vantage`
- `get_cashflow`: `local`, `yfinance`, `alpha_vantage`
- `get_income_statement`: `local`, `yfinance`, `alpha_vantage`
- `get_fundamentals`: `alpha_vantage`, `openai` (**no local today**)
- `get_news`: `local`, `google`, `openai`, `alpha_vantage` (current `local` list includes Google scraping)
- `get_global_news`: `local`, `openai` (current `local` uses Reddit datasets)
- `get_insider_sentiment`: `local`
- `get_insider_transactions`: `local`, `yfinance`, `alpha_vantage`

Offline implications:

- For a strict offline run, the offline profile MUST prevent any fallbacks to `alpha_vantage`, `google`, or `openai` (web_search).
- `get_fundamentals` currently blocks strict offline mode unless the graph is adjusted or a local implementation is added.
- `get_news` local vendor list currently includes Google scraping; strict offline mode must remove/gate that.
- `get_global_news` local implementation currently relies on Reddit JSONL datasets; for the initial offline smoke-test profile, disable `get_global_news` so no global news dataset is required.

## 4. Local data requirements (offline profile)

This section describes the local datasets required to satisfy tool calls without internet.

### 4.1 Market data (price CSV)

Used by:

- `get_stock_data` (local)
- `get_indicators` (local reads the same CSV)

Required file naming:

- `{data_dir}/market_data/price_data/NVDA-YFin-data-2015-01-01-2025-12-31.csv`

Constraint:

- local implementation rejects `end_date > 2025-12-31`.

### 4.2 Fundamentals statements (SimFin CSV)

Used by:

- `get_balance_sheet` (local)
- `get_cashflow` (local)
- `get_income_statement` (local)
- (planned) local `get_fundamentals` aggregation

Required files (separator `;`):

- `{data_dir}/fundamental_data/simfin_data_all/balance_sheet/companies/us/us-balance-quarterly.csv`
- `{data_dir}/fundamental_data/simfin_data_all/cash_flow/companies/us/us-cashflow-quarterly.csv`
- `{data_dir}/fundamental_data/simfin_data_all/income_statements/companies/us/us-income-quarterly.csv`

### 4.3 News/insider datasets (Finnhub; global news disabled)

Current code paths:

- company news: Finnhub local JSON (`finnhub_data/news_data/*_data_formatted.json`)
- insider sentiment/transactions: Finnhub local JSON (`finnhub_data/insider_*/*_data_formatted.json`)
- global/macro news: `get_global_news` tool disabled in the offline smoke-test profile

Note: you can fetch/store raw Finnhub data as JSONL/CSV for staging, but the current Finnhub local implementations read date-keyed JSON dictionaries from disk (`*_data_formatted.json`).

Smoke-test window for `curr_date=2025-12-01`:

- company news: cover at least `2025-11-24` → `2025-12-01`
- insider datasets: cover at least `2025-11-16` → `2025-12-01` (15-day lookback)
- global news: cover at least the same 7-day window (for the chosen local strategy)

## 5. Recommended offline configuration knobs

For an offline run, treat these as explicit inputs:

- `backend_url`: internal OpenAI-compatible endpoint (chat + embeddings)
- `embedding_model`: intranet embedding model name
- `data_dir`: local dataset root path
- `data_vendors`: set all categories to `local`
- `tool_vendors` overrides (recommended):
  - pin `get_news` to an offline-safe local strategy (no Google scraping)
  - pin `get_global_news` to an offline-safe local strategy (no web_search)
