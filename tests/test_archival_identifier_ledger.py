from src.archival_identifier_ledger import (
    archival_identifier_context,
    extract_archival_identifier_ledger,
)


def test_extract_archival_identifier_ledger_preserves_exact_spans() -> None:
    text = "\n".join(
        [
            "The packet references Exhibit C-1 and Docket No. P-26-1247.",
            "At 14:02:51, Pyxis MedStation 4000 recorded ORD-882341.",
            "The catalog identifier was MS-Hennessy-068.",
        ]
    )

    ledger = extract_archival_identifier_ledger(text)
    exact = {item["exact"] for item in ledger["identifiers"]}

    assert "Exhibit C-1" in exact
    assert "Docket No. P-26-1247" in exact
    assert "14:02:51" in exact
    assert "Pyxis MedStation 4000" in exact
    assert "ORD-882341" in exact
    assert "MS-Hennessy-068" in exact


def test_archival_identifier_context_is_guidance_not_truth() -> None:
    ledger = extract_archival_identifier_ledger("Exhibit M-3 records MS-Hennessy-068.")

    context = "\n".join(archival_identifier_context(ledger))

    assert "not truth" in context
    assert "Do not infer ownership" in context
    assert "Exhibit M-3" in context
