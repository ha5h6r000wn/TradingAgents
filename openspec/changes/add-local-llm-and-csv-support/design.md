## Context

This repository orchestrates multiple analysts via `TradingAgentsGraph`, each of which can call tool functions (market data, indicators, fundamentals, news, memory embeddings). In intranet environments:

- Public internet is not reachable (or not allowed).
- The LLM backend is an internal, OpenAI-compatible endpoint (`base_url`), and embeddings may be served by the same or a separate internal endpoint.
- The framework's "vendor routing" will attempt fallbacks if a primary vendor fails. If local data is incomplete, it will fall back to online vendors and fail in intranet environments.

Current observations (from repo analysis and local plans):

- `data_dir` defaults to a machine-local path and must be overridden per environment.
- `get_fundamentals` has no `local` vendor mapping today, but the default graph includes the fundamentals analyst and tool node.
- Local news "sources" may still attempt Google scraping if included in the local vendor list, and `get_global_news` currently relies on Reddit datasets.
- Some local tools hardcode filename/date constraints (e.g., price CSV range ending at `2025-12-31`).

## Goals / Non-Goals

**Goals:**

- Make `python main.py` run end-to-end in an intranet environment using:
  - internal OpenAI-compatible chat completions
  - internal (or offline) embeddings
  - local data files only
- Define a minimal offline dataset package that is verifiable with simple checks.
- Fail fast when offline prerequisites are missing (clear error instead of deep runtime failures).
- Avoid public internet requests during an offline run (including accidental fallbacks).

**Non-Goals:**

- Building a perfect offline data ingestion platform.
- Replacing the existing vendor routing system.
- Achieving parity with all online vendors (quality can improve later; first objective is "runs reliably").

## Decisions

### Decision 1: Treat intranet LLM backends as OpenAI-compatible services

Use existing configuration keys:

- `backend_url` for chat completions (LangChain `ChatOpenAI(base_url=...)`)
- `embedding_backend_url` (optional) and `embedding_model` for embeddings

Rationale: minimize changes and keep configuration explicit.

### Decision 2: Define a "local data pack" contract (directory + formats)

Define a minimal set of files under `config["data_dir"]` that guarantees local vendor success for the default analyst set, at least for a known-good ticker/date (e.g., `NVDA`, `2025-12-01`).

Rationale: local mode only works if local data is actually present; the current code otherwise falls back to online vendors.

### Decision 3: Provide a `local` implementation for `get_fundamentals`

Implement a local fundamentals report generator using existing local datasets (SimFin statements and local price CSV).

Rationale: the default graph includes the fundamentals analyst and its tool node; without a local fundamentals implementation, offline runs cannot be robust.

### Decision 4: Remove or gate public-internet scraping from "local" news

Ensure the local news vendor list does not include implementations that scrape public internet (e.g., Google News) during offline runs.

Rationale: "local" must actually mean offline; failures should not be "caught and ignored" while still attempting public internet calls.

In the offline profile for this change, prefer locally cached Finnhub datasets for:

- company news (`get_news`)
- insider sentiment / transactions

Today, `get_global_news` local implementation reads from Reddit JSONL files; if Reddit is not desired, this requires either a configuration change (to avoid calling the tool) or adding an alternative local global news implementation.

For the initial intranet smoke-test profile in this change, prefer to avoid calling `get_global_news` entirely to remove the Reddit dependency.

### Decision 5: Add a preflight to fail fast before agent execution

Introduce a preflight step that validates:

- LLM endpoints are reachable and support required APIs (chat + embeddings)
- Required files exist and can be parsed for a chosen ticker/date

Rationale: eliminates a large class of special-case runtime failures and avoids wasting time inside long agent runs.

## Risks / Trade-offs

- **Risk: Incomplete local data causes online fallbacks** → Mitigation: preflight validation + ensure minimal dataset completeness for the chosen smoke-test.
- **Risk: Embeddings endpoint not available internally** → Mitigation: support separate `embedding_backend_url` and allow a local/offline embedding fallback if needed.
- **Risk: Hardcoded local filename/date assumptions** → Mitigation: document constraints now; consider making them configurable later.
- **Risk: Ticker-specific logic (e.g., Reddit keyword mapping)** → Mitigation: scope initial smoke-test to supported tickers (e.g., NVDA) and document extension steps.
