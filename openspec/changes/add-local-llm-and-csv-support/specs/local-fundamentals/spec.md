## ADDED Requirements

### Requirement: Local fundamentals tool is available offline

The system SHALL provide a `local` vendor implementation for `get_fundamentals(ticker, curr_date)` that:

- runs without public internet access,
- uses only files under `config["data_dir"]`,
- produces a human-readable fundamentals report suitable for the fundamentals analyst.

#### Scenario: Fundamentals report is generated from local statements

- **WHEN** `get_fundamentals("NVDA", "2025-12-01")` is called in offline mode
- **AND** SimFin statement files exist under `data_dir`
- **THEN** the tool returns a non-empty string report
- **AND** the report includes:
  - an "as of" date matching `curr_date`
  - the most recently publishable statement date at or before `curr_date`
  - a clear note of data sources used (e.g., SimFin statements, local price CSV)

#### Scenario: Missing local fundamentals data is reported clearly

- **WHEN** local statement files are missing or contain no publishable rows for the given ticker/date
- **THEN** the tool SHALL return an explicit message describing which dataset is missing or empty
- **AND** SHALL NOT attempt to call any online vendor as part of the local implementation
