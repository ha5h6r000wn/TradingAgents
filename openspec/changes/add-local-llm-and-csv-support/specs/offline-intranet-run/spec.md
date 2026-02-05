## ADDED Requirements

### Requirement: Main script runs end-to-end in intranet offline mode

The system SHALL be able to run `python main.py` in an intranet environment such that:

- chat completions use an internal OpenAI-compatible endpoint, and
- embeddings use an internal OpenAI-compatible endpoint (same or separate), and
- all data tools are served from local files under `config["data_dir"]`, and
- no public internet data vendors are required for a successful run.

#### Scenario: NVDA offline smoke-test completes

- **WHEN** `main.py` is configured with:
  - `backend_url` pointing to an internal OpenAI-compatible endpoint
  - `embedding_model` set to an embedding model available on the intranet
  - `data_dir` pointing to a prepared local dataset pack
  - `data_vendors` configured so all categories route to `local`
- **THEN** calling `TradingAgentsGraph(debug=true).propagate("NVDA", "2025-12-01")` completes without uncaught exceptions
- **AND** returns a non-empty final decision payload

#### Scenario: Embeddings endpoint is missing or incompatible

- **WHEN** embeddings cannot be generated (endpoint unreachable or model not found)
- **THEN** the system SHALL fail fast with a clear error describing:
  - the configured `embedding_backend_url` (or `backend_url`)
  - the configured `embedding_model`
  - the failing API call type (`/embeddings`)

### Requirement: Offline mode does not rely on public internet scraping

In offline/intranet runs, the system SHALL NOT require any public internet scraping implementations as part of "local" vendors.

#### Scenario: Local news sources are offline-safe

- **WHEN** the offline configuration is enabled for news tools
- **THEN** `get_news` SHALL NOT invoke any implementation that scrapes public internet sources (e.g., Google search/news pages)
- **AND** `get_news` SHALL be satisfiable by local files in `data_dir` for the smoke-test ticker/date

#### Scenario: Global news tool is not used in the offline profile

- **WHEN** running the offline smoke-test profile
- **THEN** the graph SHALL NOT expose `get_global_news` as an available tool to the LLM
- **AND** the News Analyst toolset SHALL still include:
  - `get_news`
  - `get_insider_sentiment`
  - `get_insider_transactions`
- **AND** the run SHALL NOT depend on any global news dataset for success
