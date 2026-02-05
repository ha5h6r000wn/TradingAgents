## 1. Intranet environment prerequisites

- [ ] 1.1 Confirm internal LLM endpoint supports OpenAI-compatible chat completions (including tool/function calling).
- [ ] 1.2 Confirm an embeddings endpoint is available internally (same `backend_url` or a separate `embedding_backend_url`) and decide the `embedding_model` name.
- [ ] 1.3 Decide the intranet machine `data_dir` path and confirm read permissions for the runtime user.

## 2. Prepare the minimal local data pack (NVDA smoke-test)

- [ ] 2.1 Create the required directory tree under `data_dir` (market_data, simfin, finnhub).
- [ ] 2.2 Populate `market_data/price_data/NVDA-YFin-data-2015-01-01-2025-12-31.csv` and verify it loads with pandas.
- [ ] 2.3 Populate SimFin quarterly statement CSVs and verify required columns (`Ticker`, `Report Date`, `Publish Date`) exist.
- [ ] 2.4 Populate Finnhub company datasets for `NVDA` (news, insider_senti, insider_trans) in the expected local runtime format and verify they parse as JSON.
- [ ] 2.4.1 If collecting raw Finnhub data as JSONL/CSV, convert/group by day into the required date-keyed `*_data_formatted.json` files.
- [ ] 2.5 Configure the offline smoke-test profile so `get_global_news` is not exposed to the LLM while keeping the News Analyst tools (`get_news`, `get_insider_sentiment`, `get_insider_transactions`).

## 3. Configure `main.py` for offline/intranet run

- [ ] 3.1 Update the runtime config in `main.py` to set `backend_url`, model names, `embedding_model`, and `data_dir` for the intranet environment.
- [ ] 3.2 Update the runtime config in `main.py` to route ALL `data_vendors` categories to `local`.

## 4. Close local-mode gaps blocking offline execution

- [ ] 4.1 Add a `local` vendor implementation for `get_fundamentals` and wire it into `tradingagents/dataflows/interface.py`.
- [ ] 4.2 Ensure the offline news configuration never attempts public internet scraping during offline runs (remove or gate Google scraping; avoid Reddit dependency if not desired).
- [ ] 4.3 Add a preflight check (script or function) that validates `data_dir` completeness + embeddings availability before running the agents.

## 5. Verify end-to-end offline run

- [ ] 5.1 Run the offline smoke-test: `python main.py` with `("NVDA", "2025-12-01")` and confirm it completes with a non-empty decision.
- [ ] 5.2 Verify no public internet endpoints are contacted during the run (e.g., via network policy, proxy logs, or packet capture in the intranet environment).
