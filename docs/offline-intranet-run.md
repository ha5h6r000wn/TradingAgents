# Offline/Intranet Run Guide for `main.py`

Goal: run `python main.py` end-to-end inside an intranet environment using:

- internal OpenAI-compatible LLM endpoint (`backend_url`)
- embeddings served by the same endpoint
- local datasets under a configurable `data_dir`

This document is a human-facing runbook. The canonical requirements live under:

- `openspec/changes/add-local-llm-and-csv-support/`

## 1. What executes when `main.py` runs

The graph executes a fixed sequence of nodes (default analyst set):

1. Market Analyst
2. Social Media Analyst
3. News Analyst
4. Fundamentals Analyst
5. Bull Researcher ↔ Bear Researcher (debate loop)
6. Research Manager
7. Trader
8. Risky → Safe → Neutral (risk loop)
9. Risk Judge

Each analyst may call data tools repeatedly until it stops issuing tool calls.

For the tool inventory and routing details, see:

- `openspec/changes/add-local-llm-and-csv-support/workflow-map.md`

## 2. Minimum offline datasets (smoke-test)

Smoke-test input:

- ticker: `NVDA`
- trade date: `2025-12-01`

### 2.1 Price CSV (required)

Required file:

- `{data_dir}/market_data/price_data/NVDA-YFin-data-2015-01-01-2025-12-31.csv`

Note: local stock data rejects `end_date > 2025-12-31`.

### 2.2 SimFin statements (recommended / required for fundamentals completeness)

Required files (separator `;`):

- `{data_dir}/fundamental_data/simfin_data_all/balance_sheet/companies/us/us-balance-quarterly.csv`
- `{data_dir}/fundamental_data/simfin_data_all/cash_flow/companies/us/us-cashflow-quarterly.csv`
- `{data_dir}/fundamental_data/simfin_data_all/income_statements/companies/us/us-income-quarterly.csv`

### 2.3 Finnhub caches (recommended; required if tools are called)

Company datasets:

- `{data_dir}/finnhub_data/news_data/NVDA_data_formatted.json`
- `{data_dir}/finnhub_data/insider_senti/NVDA_data_formatted.json`
- `{data_dir}/finnhub_data/insider_trans/NVDA_data_formatted.json`

Note: you can fetch/store raw Finnhub data as JSONL/CSV (e.g., one JSON per line from the Finnhub SDK), but the current local tool implementations read the **date-keyed JSON** format shown above.

If you collect raw company news as JSONL (one item per line), convert it into the required date-keyed JSON dictionary:

- key: `YYYY-MM-DD`
- value: list of Finnhub news objects for that day (must include at least `headline` and `summary`)

### 2.4 Global news (tool disabled; keep other News tools)

The initial intranet/offline smoke-test profile disables `get_global_news` entirely, so no global news dataset is required to complete the run.

To do that, do NOT expose the `get_global_news` tool to the LLM.

However, if you still want company news and insider tools, keep the News Analyst node and expose only:

- `get_news`
- `get_insider_sentiment`
- `get_insider_transactions`

Date coverage:

- company/global news: at least `2025-11-24` → `2025-12-01`
- insider datasets: at least `2025-11-16` → `2025-12-01`

## 3. Offline configuration checklist

To run offline, configuration MUST specify:

- `backend_url` (internal OpenAI-compatible base URL)
- `embedding_model` (internal embedding model name)
- `data_dir` (local dataset root)
- `data_vendors`: all categories set to `local`

## 4. Known blockers (must be addressed for strict offline)

- `get_fundamentals` has no `local` vendor today; strict offline requires adding one or adjusting the default analyst set.
- Local news routing currently includes public internet implementations (Google scraping); strict offline must disable them.
