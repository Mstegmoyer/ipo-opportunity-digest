# AGENTS.md

## Mission
Build a production-ready Python system that sends a weekly email containing:
1. Top 5 U.S. IPO opportunities for the week
2. Top 10 U.S. finance advisory opportunities to target

This system is for a finance advisory firm focused on large, strategic finance transformations.

## Business scope

### Company universe
Include only:
- U.S.-based Fortune 1000 companies
- U.S.-based public or private companies with annual revenue > $2B
- U.S.-based PE-backed or PE-owned companies only when clearly large-scale and strategically relevant

### Priority opportunity types
- IPO readiness / IPO support / S-1 / F-1 / listing readiness
- M&A / acquisition / sale / integration / carve-out / divestiture
- ERP / EPM / consolidation / close / reporting / finance systems transformation
- Restructuring / layoffs / operating model shifts
- Process enhancements / finance analysis / data modernization / governance / analytics enablement
- Capital markets activity
- Material weakness / restatement / adverse SEC findings
- Regulatory / ESG reporting modernization
- Significant capex / facility programs with finance implications
- Advisory RFPs or disclosed transformation efforts

### Specific project themes to emphasize
- Systems Implementation
- S/4HANA Implementation Support
- Microsoft Dynamics AX Reporting Buildout
- Mergers / Integrations / Migrations
- Divestitures / Carve-Outs
- Process Enhancements & Analysis
- IPO Readiness / IPO Support
- Pre-IPO Analysis & Scoring
- Restructuring Projects

### Explicit exclusions
Do not include:
- routine audit support
- routine 10-K / 10-Q work unless tied to IPO, restatement, or material weakness
- basic staff augmentation
- non-strategic backfills
- month-end help unless tied to a transformation trigger
- companies outside the qualification rules unless clearly strategic and justified

## Required output behavior

### Weekly deliverables
A. Top 5 U.S. IPOs this week
B. Top 10 U.S. target opportunities

### Opportunity recency buckets
Use exactly:
- 0–30 days
- 31–90 days
- >90 days

### Final ranking rule
Do NOT let the model freely pick the final top 10.
Instead:
1. Collect raw candidate opportunities
2. Apply deterministic qualification filters
3. Score all qualified candidates in code
4. Select the top shortlist in code
5. Use the model only to summarize/classify/map the finalists

The model is not the source of truth for ranking.

## Required columns for tabular exports
For the Top 10 opportunities table, use:
- Bucket
- Company name
- Website
- CFO
- CAO
- Initiative type
- Timeline
- Summary
- Role we could fill
- Source
- Score

For the IPO table, use:
- Company name
- Website
- IPO signal
- Date
- Why it matters
- Role we could fill
- Source
- Score

## Data quality rules
- Every final row must include at least one source URL
- Preserve publication date or filing date
- Prefer primary sources first
- Deduplicate by official company name
- If CFO or CAO is unclear, write: Unknown (as of YYYY-MM-DD)
- If revenue is uncertain, write: Unknown (as of YYYY-MM-DD) and reduce confidence
- Avoid repeat alerts unless there is a materially new trigger
- Summaries must be concise and business-ready
- Final summaries should not exceed 40 words in tabular outputs

## Our offerings / role we could fill
- Budgeting & Forecasting
- Consolidations
- Controllership
- Divestitures / Carve-Outs
- External Audit
- Financial Reporting
- Financial Restatements
- GL / Month-End Close
- IPO Readiness
- M&A Integration
- Management Reporting
- Process Improvement
- Project Management
- Restructuring
- SEC & Regulatory Reporting
- SOX / Internal Audit / Controls
- System Implementation
- Tax Research & Reporting
- Technical Accounting

## Scoring framework
Implement a deterministic weighted scoring model from 0 to 100 using:
- trigger_strength (0–25)
- company_qualification_fit (0–20)
- enterprise_scale_strategic_relevance (0–15)
- offering_alignment (0–20)
- recency (0–10)
- source_confidence (0–10)

Suggested interpretation:
- 85–100 = very strong target
- 70–84 = strong target
- 55–69 = watchlist / near miss
- below 55 = generally exclude unless manually overridden

## Coding standards
- Python 3.11+
- strong typing
- modular design
- clear logging
- dataclasses or pydantic models
- deterministic filters before model summarization
- environment variables for secrets
- unit tests for scoring, qualification, dedupe, and rendering
- simple, maintainable code over clever abstractions

## Deliverables
The repository must include:
- README.md
- requirements.txt
- .env.example
- src/
- tests/
- templates/
- sample JSON output
- sample CSV output
- GitHub Actions workflow
- manual run support
