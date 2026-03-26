"""
session_manager.py

Tracks per-session request history in memory.
No persistence — data is lost on restart, which is fine for this use case.
"""

import threading
from datetime import datetime


class SessionManager:

    def __init__(self):
        self._lock     = threading.Lock()
        self._sessions: dict[str, dict] = {}

    def record_request(self, session_id: str, sector: str):
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "session_id":    session_id,
                    "created_at":    datetime.utcnow().isoformat(),
                    "request_count": 0,
                    "sectors":       [],
                }
            s = self._sessions[session_id]
            s["request_count"] += 1
            s["sectors"].append({"sector": sector, "at": datetime.utcnow().isoformat()})
            s["last_active"] = datetime.utcnow().isoformat()

    def get_session(self, session_id: str) -> dict | None:
        return self._sessions.get(session_id)

    def count(self) -> int:
        return len(self._sessions)
