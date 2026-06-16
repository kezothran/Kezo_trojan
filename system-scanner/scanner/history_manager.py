"""
History manager: persist scan results to JSON on disk.
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from scanner.constants import HISTORY_FILE, MAX_HISTORY_ENTRIES


class HistoryManager:
    """Manages scan history stored as a JSON file."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.filepath = os.path.join(data_dir, HISTORY_FILE)
        os.makedirs(data_dir, exist_ok=True)

    def load(self) -> list[dict]:
        """Load history from file. Returns a list of scan session dicts."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, IOError):
            return []

    def save(self, history: list[dict]):
        """Write history list to file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save history: {e}")

    def add_session(self, target: str, port_range: str, results: list[dict]):
        """Add a scan session to history."""
        history = self.load()

        session = {
            "id": len(history) + 1,
            "target": target,
            "port_range": port_range,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result_count": len(results),
            "results": results,
        }

        history.append(session)

        # Trim old entries
        if len(history) > MAX_HISTORY_ENTRIES:
            history = history[-MAX_HISTORY_ENTRIES:]

        self.save(history)
        return session

    def get_latest(self, count: int = 10) -> list[dict]:
        """Get the latest N sessions."""
        history = self.load()
        return history[-count:]

    def clear(self):
        """Clear all history."""
        self.save([])
