# IPO Opportunity Digest

Production-ready scaffold for a weekly email system that sends:
1. Top 5 U.S. IPO opportunities for the week
2. Top 10 U.S. finance transformation opportunities across qualified U.S. enterprises

## Scope alignment

This scaffold implements deterministic qualification and scoring foundations aligned to repository `AGENTS.md`:
- Qualification filters for U.S.-based Fortune 1000 / >$2B revenue / qualified large-scale PE-backed targets
- Weighted 0–100 scoring model with required component buckets
- Deterministic shortlist selection in code (model not used for ranking)
- Jinja2 weekly email template with required columns

## Project structure

```text
.
├── data/
│   └── samples/
│       ├── ipos.json
│       └── opportunities.json
├── sample_output/
│   ├── sample_digest.csv
│   ├── sample_digest.html
│   └── sample_digest.json
├── src/
├── templates/
└── tests/
```

## Exact local test commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
pytest -vv
pytest tests/test_scoring.py -vv
```

## Exact local dry-run / export commands

```bash
# Generates HTML + JSON + CSV previews and never sends email
python -m src.main --dry-run

# Writes only preview files (no HTML stdout)
python -m src.main --export-only

# Uses deterministic fixtures + fixed date for stable test outputs
python -m src.main --test-mode
```

## Exact cloud/CI test commands

The GitHub Actions workflow runs:

```bash
pytest
python -m src.main --dry-run > /tmp/digest.html
```

## Safety behavior

- Email sending is **disabled automatically** in `--dry-run` and `--export-only` modes.
- Email is only attempted when `--send-email` is explicitly passed **and** not in dry/export mode.

## What is intentionally not implemented yet

- Live data-source adapters (SEC/news/RSS/vendor APIs)
- Production-grade secrets management and email retry policies
- LLM summarization/classification step for finalists
