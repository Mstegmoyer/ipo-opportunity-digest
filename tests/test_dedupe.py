from datetime import date

from src.dedupe import dedupe_ipos_by_company, dedupe_opportunities_by_company
from src.sources.ipo_calendar import collect_ipo_calendar
from src.sources.press_releases import collect_press_release_opportunities


def test_dedupe_opportunities_keeps_latest_trigger_date(sample_opportunities_records) -> None:
    items = collect_press_release_opportunities(sample_opportunities_records["press_release_records"])
    older = items[0]
    newer = type(older)(
        company_name=older.company_name.lower(),
        website=older.website,
        company_qualification=older.company_qualification,
        initiative_type=older.initiative_type,
        trigger_date=date(2026, 4, 10),
        timeline=older.timeline,
        summary=older.summary,
        role_we_could_fill=older.role_we_could_fill,
        source_urls=older.source_urls,
        trigger_keywords=older.trigger_keywords,
        cfo=older.cfo,
        cao=older.cao,
        is_us_based=older.is_us_based,
        publication_date=date(2026, 4, 10),
    )

    deduped = dedupe_opportunities_by_company([older, newer])
    assert len(deduped) == 1
    assert deduped[0].trigger_date == date(2026, 4, 10)


def test_dedupe_ipos_keeps_latest_signal_date(sample_ipos_records) -> None:
    items = collect_ipo_calendar(sample_ipos_records["ipo_calendar_records"])
    older = items[0]
    newer = type(older)(
        company_name=older.company_name.lower(),
        ipo_signal=older.ipo_signal,
        date=date(2026, 4, 9),
        why_it_matters=older.why_it_matters,
        role_we_could_fill=older.role_we_could_fill,
        source_urls=older.source_urls,
        company_qualification=older.company_qualification,
        website=older.website,
        is_us_based=older.is_us_based,
    )

    deduped = dedupe_ipos_by_company([older, newer])
    assert len(deduped) == 1
    assert deduped[0].date == date(2026, 4, 9)
