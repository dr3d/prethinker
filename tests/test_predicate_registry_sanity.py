import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_general_predicate_registry_sanity():
    path = ROOT / "modelfiles" / "predicate_registry.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("canonical_predicates", [])
    assert isinstance(rows, list)
    seen: set[tuple[str, int]] = set()
    saw_at_step = False
    for row in rows:
        assert isinstance(row, dict)
        name = str(row.get("name", "")).strip()
        arity = int(row.get("arity", -1))
        assert name
        assert arity >= 0
        key = (name, arity)
        assert key not in seen
        seen.add(key)
        if key == ("at_step", 2):
            saw_at_step = True
    assert saw_at_step
