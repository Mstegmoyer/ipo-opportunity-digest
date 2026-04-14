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
├── .env.example
├── .github/workflows/weekly_digest.yml
├── requirements.txt
├── sample_output/
│   ├── sample_digest.csv
│   └── sample_digest.json
├── src/
│   ├── config.py
│   ├── constants.py
│   ├── main.py
│   ├── models.py
│   ├── qualify.py
│   ├── rendering.py
│   ├── scoring.py
│   └── selectors.py
├── templates/
│   └── weekly_digest.html.j2
└── tests/
    ├── test_qualify.py
    ├── test_rendering.py
    ├── test_scoring.py
    └── test_selectors.py
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest
python -m src.main
```

## What is intentionally not implemented yet

- Live data-source adapters (SEC/news/RSS/vendor APIs)
- Production email transport integration
- LLM summarization/classification step for finalists

## Next implementation milestones

1. Add source adapters that normalize opportunities into `src.models`.
2. Persist raw/source metadata and publication dates.
3. Enforce summary length trimming for table outputs (<=40 words).
4. Add CSV/JSON export pipeline and SMTP sender.
5. Schedule weekly run via GitHub Actions and/or managed orchestrator.
