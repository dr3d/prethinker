from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Any


DATA_BASE_URL = "https://data.sec.gov"
ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
DEFAULT_CACHE_DIR = Path("datasets") / "sec_edgar" / "generated" / "cache"


class SecEdgarClient:
    """Small SEC EDGAR client for reproducible source-slice experiments."""

    def __init__(
        self,
        *,
        user_agent: str | None = None,
        data_base_url: str = DATA_BASE_URL,
        cache_dir: Path | str = DEFAULT_CACHE_DIR,
    ) -> None:
        self.user_agent = user_agent if user_agent is not None else os.environ.get("SEC_USER_AGENT", "")
        self.data_base_url = str(data_base_url or DATA_BASE_URL).rstrip("/")
        self.cache_dir = Path(cache_dir)

    def submissions(self, cik: str | int) -> dict[str, Any]:
        cik10 = _cik10(cik)
        return self.get_json(f"/submissions/CIK{cik10}.json")

    def company_facts(self, cik: str | int) -> dict[str, Any]:
        cik10 = _cik10(cik)
        return self.get_json(f"/api/xbrl/companyfacts/CIK{cik10}.json")

    def get_json(self, path: str) -> dict[str, Any]:
        if not self.user_agent:
            raise RuntimeError("SEC_USER_AGENT is required for live SEC EDGAR API calls.")
        clean_path = "/" + str(path or "").strip("/")
        url = f"{self.data_base_url}{clean_path}"
        cached = self._cache_path(url)
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8"))
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent, "Accept-Encoding": "gzip, deflate"})
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"


def archive_document_url(*, cik: str | int, accession_number: str, primary_document: str) -> str:
    cik_int = str(int(str(cik).strip()))
    accession_clean = str(accession_number or "").replace("-", "").strip()
    document = str(primary_document or "").strip()
    return f"{ARCHIVES_BASE_URL}/{cik_int}/{accession_clean}/{document}"


def _cik10(cik: str | int) -> str:
    digits = "".join(ch for ch in str(cik or "") if ch.isdigit())
    if not digits:
        raise ValueError("CIK is required")
    return digits.zfill(10)
