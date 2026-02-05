## ADDED Requirements

### Requirement: Define the local data directory contract

The system SHALL define a required directory structure under `config["data_dir"]` that is sufficient to run the offline smoke-test (`NVDA`, `2025-12-01`) without public internet access.

#### Scenario: Required directories exist

- **WHEN** `data_dir` is set for an offline run
- **THEN** the following directories MUST exist:
  - `market_data/price_data/`
  - `fundamental_data/simfin_data_all/`
  - `finnhub_data/`
  - `finnhub_data/news_data/`
  - `finnhub_data/insider_senti/`
  - `finnhub_data/insider_trans/`

### Requirement: Local market price CSV file exists and matches naming constraints

Local market data SHALL be available via CSV files with the naming convention expected by local vendors.

#### Scenario: NVDA price CSV is present

- **WHEN** running the offline smoke-test for `NVDA` in the date range `2015-01-01` to `2025-12-31`
- **THEN** the file `market_data/price_data/NVDA-YFin-data-2015-01-01-2025-12-31.csv` MUST exist under `data_dir`
- **AND** the CSV MUST include at least the columns: `Date`, `Open`, `High`, `Low`, `Close`

### Requirement: SimFin statement CSV files exist and include required columns

Local fundamentals statements SHALL be available via SimFin CSV files.

#### Scenario: SimFin quarterly statements exist

- **WHEN** running fundamentals tools in offline mode
- **THEN** the following files MUST exist under `data_dir`:
  - `fundamental_data/simfin_data_all/balance_sheet/companies/us/us-balance-quarterly.csv`
  - `fundamental_data/simfin_data_all/cash_flow/companies/us/us-cashflow-quarterly.csv`
  - `fundamental_data/simfin_data_all/income_statements/companies/us/us-income-quarterly.csv`
- **AND** each CSV MUST include the columns: `Ticker`, `Report Date`, `Publish Date`

### Requirement: Finnhub local JSON files exist for news and insider datasets

Offline news/insider tools MAY be staged in CSV or JSON, but the runtime format SHALL match what the current local tool implementations can read.

Today, Finnhub local implementations read date-keyed JSON dictionaries from disk.

#### Scenario: Finnhub-formatted local files exist for NVDA

- **WHEN** `get_news`, `get_insider_sentiment`, or `get_insider_transactions` are called for `NVDA`
- **THEN** the following files MUST exist under `data_dir`:
  - `finnhub_data/news_data/NVDA_data_formatted.json`
  - `finnhub_data/insider_senti/NVDA_data_formatted.json`
  - `finnhub_data/insider_trans/NVDA_data_formatted.json`
- **AND** each file MUST be valid JSON and loadable without network access

#### Scenario: Raw Finnhub exports can be stored as JSONL/CSV (staging)

- **WHEN** collecting Finnhub data via API during data preparation
- **THEN** raw exports MAY be stored as JSONL and/or CSV for auditability
- **AND** the data pack preparation MUST still produce the runtime `*_data_formatted.json` files above (date-keyed dictionaries)

### Requirement: Offline profile does not require global news datasets

The offline smoke-test profile SHALL NOT require any global news dataset for success.

#### Scenario: `get_global_news` is not used

- **WHEN** running the offline smoke-test profile
- **THEN** no global news dataset is required under `data_dir`
