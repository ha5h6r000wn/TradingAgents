## Why

Running `main.py` inside an intranet environment currently fails or becomes nondeterministic because parts of the pipeline still depend on public internet data vendors (e.g., Alpha Vantage / Google) and because the "local" dataset is not fully specified/prepared.

We need a clear offline contract (data + config) so that `main.py` can run end-to-end using internal OpenAI-compatible LLM endpoints and local files only.

## What Changes

- Define an intranet/offline run contract for `main.py` (LLM endpoints + configuration knobs).
- Define a minimal, verifiable local dataset package required to run the default analyst set end-to-end.
- Close the local-mode gaps that currently prevent offline execution:
  - Provide a `local` implementation for `get_fundamentals`.
  - Ensure local news sources do not perform public internet scraping during offline runs.
- Add a lightweight preflight that fails fast with a clear "missing files / misconfig" error before invoking agents.
- Document a step-by-step runbook to prepare data and validate the environment.

## Capabilities

### New Capabilities

- `offline-intranet-run`: Run `python main.py` fully offline using internal LLM endpoints and local data without public internet dependencies.
- `local-data-pack`: Define the required `data_dir` directory structure and file formats for the minimal offline dataset.
- `local-fundamentals`: Provide an offline `get_fundamentals` implementation backed by local fundamentals data.

### Modified Capabilities

- (none)

## Impact

- `main.py`: configuration updates for offline/intranet runs (LLM + `data_dir` + vendor selection).
- `tradingagents/dataflows/interface.py`: ensure local routing supports offline execution (including `get_fundamentals` and news sources).
- `tradingagents/dataflows/local.py`: implement offline fundamentals aggregation and/or validations as needed.
- Local data folder at `config["data_dir"]`: new required datasets (CSV/JSON/JSONL) for offline runs.
