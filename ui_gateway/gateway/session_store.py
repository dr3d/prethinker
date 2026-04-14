from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class SessionState:
    session_id: str
    created_at: float = field(default_factory=time.time)
    turns: list[dict] = field(default_factory=list)
    pending_clarification: dict | None = None


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}

    def get_or_create(self, session_id: str | None = None) -> SessionState:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        new_id = session_id or f"session-{uuid.uuid4().hex[:10]}"
        state = SessionState(session_id=new_id)
        self._sessions[new_id] = state
        return state

    def reset(self, session_id: str | None = None) -> SessionState:
        state = self.get_or_create(session_id)
        state.turns.clear()
        state.pending_clarification = None
        return state

    def get(self, session_id: str | None = None) -> SessionState | None:
        key = str(session_id or "").strip()
        if not key:
            return None
        return self._sessions.get(key)

    def snapshot(self, session_id: str | None = None) -> dict | None:
        state = self.get(session_id)
        if state is None:
            return None
        return {
            "session_id": state.session_id,
            "created_at": state.created_at,
            "turn_count": len(state.turns),
            "pending_clarification": state.pending_clarification,
            "turns": state.turns,
        }
