from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://www.courtlistener.com/api/rest/v4"
DEFAULT_CACHE_DIR = Path("datasets") / "courtlistener" / "generated" / "cache"


class CourtListenerClient:
    """Tiny conservative CourtListener REST client.

    The client is intentionally small: first-pass experiments should fetch a
    reproducible slice and cache raw responses, not attempt bulk ingestion.
    """

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        cache_dir: Path | str = DEFAULT_CACHE_DIR,
    ) -> None:
        self.api_token = api_token if api_token is not None else os.environ.get("COURTLISTENER_API_TOKEN", "")
        self.base_url = str(base_url or DEFAULT_BASE_URL).rstrip("/")
        self.cache_dir = Path(cache_dir)

    def search(self, *, q: str, type: str = "o", page_size: int = 10, **params: Any) -> dict[str, Any]:
        query = {"q": q, "type": type, "page_size": str(page_size), **{k: v for k, v in params.items() if v is not None}}
        return self.get_json("/search/", query)

    def get_opinion(self, opinion_id: str | int) -> dict[str, Any]:
        return self.get_json(f"/opinions/{opinion_id}/")

    def get_docket(self, docket_id: str | int) -> dict[str, Any]:
        return self.get_json(f"/dockets/{docket_id}/")

    def citation_lookup(self, *, text: str) -> list[dict[str, Any]]:
        """Call CourtListener's citation lookup endpoint.

        This is token-gated and cached like the other live calls. It is not used
        by the legal verification tests unless an explicit live fixture is
        added; the research lane's claim path should remain reproducible from
        checked-in inventories.
        """

        url = self._url("/citation-lookup/", {})
        body = urllib.parse.urlencode({"text": text}).encode("utf-8")
        payload = self._request_json(
            method="POST",
            url=url,
            body=body,
            extra_headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        raise RuntimeError("Unexpected CourtListener citation lookup response shape.")

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._url(path, params or {})
        payload = self._request_json(method="GET", url=url)
        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected CourtListener JSON response shape.")
        return payload

    def _request_json(
        self,
        *,
        method: str,
        url: str,
        body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        cached = self._cache_path(method=method, url=url, body=body)
        if cached.exists():
            return json.loads(cached.read_text(encoding="utf-8"))
        if not self.api_token:
            raise RuntimeError("COURTLISTENER_API_TOKEN is required for live CourtListener API calls.")
        headers = {"Authorization": f"Token {self.api_token}", **(extra_headers or {})}
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def _url(self, path: str, params: dict[str, Any]) -> str:
        clean_path = "/" + str(path or "").strip("/")
        query = urllib.parse.urlencode({k: str(v) for k, v in sorted(params.items())})
        return f"{self.base_url}{clean_path}" + (f"?{query}" if query else "")

    def _cache_path(self, *, method: str, url: str, body: bytes | None = None) -> Path:
        cache_key = method.upper().encode("utf-8") + b"\0" + url.encode("utf-8") + b"\0" + (body or b"")
        digest = hashlib.sha256(cache_key).hexdigest()
        return self.cache_dir / f"{digest}.json"
