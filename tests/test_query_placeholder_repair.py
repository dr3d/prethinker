from scripts.run_domain_bootstrap_qa import _placeholder_repaired_query


def test_placeholder_repair_converts_compact_state_value_labels_to_variables() -> None:
    repaired = _placeholder_repaired_query("current_lease_state(Leaseid, currentrent, Expirydate).")

    assert repaired == {
        "query": "current_lease_state(Leaseid, Currentrent, Expirydate).",
        "repairs": [{"index": 2, "from": "currentrent", "to": "Currentrent"}],
    }


def test_placeholder_repair_converts_temporal_expiry_label_to_variable() -> None:
    repaired = _placeholder_repaired_query("current_lease_state(Leaseid, rent, expiry).")

    assert repaired == {
        "query": "current_lease_state(Leaseid, Rent, Expiry).",
        "repairs": [
            {"index": 2, "from": "rent", "to": "Rent"},
            {"index": 3, "from": "expiry", "to": "Expiry"},
        ],
    }


def test_placeholder_repair_keeps_specific_constants() -> None:
    assert _placeholder_repaired_query("lease_tenant(Leaseid, kettner_associates).") is None
    assert _placeholder_repaired_query("lease_status(Leaseid, active).") is None
    assert _placeholder_repaired_query("event_date(Event, april_2024).") is None
