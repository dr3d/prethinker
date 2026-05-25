"""Local filesystem storage for the public Engine API."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from prethinker.models import KBMetadata, SourceRecord


class LocalKBStore:
    """Small JSONL-backed KB registry used by the alpha Engine facade."""

    def __init__(self, storage_dir: str | Path) -> None:
        self.storage_dir = Path(storage_dir)

    def is_ready(self) -> bool:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        probe = self.storage_dir / ".ready"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True

    def create_kb(
        self,
        *,
        document_name: str,
        document_type: str,
        document_bytes: bytes,
        source_records: list[SourceRecord],
    ) -> KBMetadata:
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(document_name.encode("utf-8") + b"\0" + document_bytes).hexdigest()
        kb_id = f"kb_{digest[:16]}"
        kb_dir = self._kb_dir(kb_id)
        kb_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).isoformat()
        metadata = KBMetadata(
            kb_id=kb_id,
            document_name=document_name,
            document_type=document_type,
            created_at=now,
            updated_at=now,
            source_record_count=len(source_records),
            metadata={"schema_version": "prethinker_public_kb_metadata_v1"},
        )
        records = [SourceRecord(record_id=row.record_id, kb_id=kb_id, payload=dict(row.payload)) for row in source_records]

        (kb_dir / "source.bin").write_bytes(document_bytes)
        (kb_dir / "metadata.json").write_text(json.dumps(metadata.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        with (kb_dir / "source_records.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
        return metadata

    def list_kbs(self) -> list[KBMetadata]:
        if not self.storage_dir.exists():
            return []
        items = [metadata for path in self.storage_dir.iterdir() if path.is_dir() for metadata in [self._read_metadata(path)] if metadata]
        items.sort(key=lambda item: (item.created_at, item.kb_id))
        return items

    def get_kb(self, kb_id: str) -> KBMetadata | None:
        return self._read_metadata(self._kb_dir(kb_id))

    def load_kb(self, kb_id: str) -> tuple[KBMetadata, list[SourceRecord]] | None:
        metadata = self.get_kb(kb_id)
        if metadata is None:
            return None
        records_path = self._kb_dir(kb_id) / "source_records.jsonl"
        records: list[SourceRecord] = []
        if records_path.exists():
            for line in records_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                records.append(
                    SourceRecord(
                        record_id=str(payload["record_id"]),
                        kb_id=str(payload["kb_id"]),
                        payload=dict(payload.get("payload") or {}),
                    )
                )
        return metadata, records

    def delete_kb(self, kb_id: str) -> bool:
        kb_dir = self._kb_dir(kb_id)
        if not kb_dir.exists():
            return False
        root = self.storage_dir.resolve()
        target = kb_dir.resolve()
        if root != target and root not in target.parents:
            raise ValueError(f"refusing to delete outside storage_dir: {target}")
        shutil.rmtree(target)
        return True

    def _kb_dir(self, kb_id: str) -> Path:
        if not kb_id or "/" in kb_id or "\\" in kb_id or ".." in kb_id:
            raise ValueError("invalid kb_id")
        return self.storage_dir / kb_id

    def _read_metadata(self, kb_dir: Path) -> KBMetadata | None:
        path = kb_dir / "metadata.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return KBMetadata(
            kb_id=str(data["kb_id"]),
            document_name=str(data["document_name"]),
            document_type=str(data["document_type"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            source_record_count=int(data["source_record_count"]),
            metadata=dict(data.get("metadata") or {}),
        )
