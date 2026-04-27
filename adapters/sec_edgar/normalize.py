from __future__ import annotations

from typing import Any

from adapters.sec_edgar.client import archive_document_url
from adapters.sec_edgar.models import FilingSourceRecord


def normalize_submission_filing(submission: dict[str, Any], index: int) -> FilingSourceRecord:
    recent = submission.get("filings", {}).get("recent", {}) if isinstance(submission.get("filings"), dict) else {}
    company_name = str(submission.get("name") or "").strip() or None
    cik = str(submission.get("cik") or "").strip() or None

    def at(key: str) -> str | None:
        values = recent.get(key, []) if isinstance(recent, dict) else []
        if not isinstance(values, list) or index >= len(values):
            return None
        text = str(values[index] or "").strip()
        return text or None

    accession = at("accessionNumber")
    form_type = at("form")
    filing_date = at("filingDate")
    report_date = at("reportDate")
    primary_document = at("primaryDocument")
    source_id = accession or f"{cik or 'unknown'}-{index}"
    provenance_url = None
    if cik and accession and primary_document:
        provenance_url = archive_document_url(cik=cik, accession_number=accession, primary_document=primary_document)
    return FilingSourceRecord(
        source="sec_edgar",
        source_kind="filing",
        source_id=source_id,
        company_name=company_name,
        cik=cik,
        accession_number=accession,
        form_type=form_type,
        filing_date=filing_date,
        report_date=report_date,
        primary_document=primary_document,
        exhibit_type=None,
        text_excerpt="",
        provenance_url=provenance_url,
        metadata={"sic": submission.get("sic"), "tickers": submission.get("tickers", [])},
    )


def normalize_contract_excerpt(
    *,
    source_id: str,
    company_name: str,
    cik: str,
    accession_number: str,
    form_type: str,
    filing_date: str,
    primary_document: str,
    text_excerpt: str,
    exhibit_type: str = "EX-10",
) -> FilingSourceRecord:
    return FilingSourceRecord(
        source="sec_edgar",
        source_kind="contract_excerpt",
        source_id=str(source_id),
        company_name=str(company_name),
        cik=str(cik),
        accession_number=str(accession_number),
        form_type=str(form_type),
        filing_date=str(filing_date),
        report_date=None,
        primary_document=str(primary_document),
        exhibit_type=str(exhibit_type),
        text_excerpt=str(text_excerpt).strip(),
        provenance_url=archive_document_url(
            cik=cik,
            accession_number=accession_number,
            primary_document=primary_document,
        ),
        metadata={},
    )
