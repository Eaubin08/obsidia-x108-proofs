"""Reference students, executed inside the isolated container. No bench, no data import."""
from __future__ import annotations

import json

HOLD = "HOLD"


class StateIntegrityError(Exception):
    """Raised by load() when the saved state was altered."""


class EmptyStudent:
    """No knowledge, no learning: answers HOLD everywhere (RED reference)."""

    def learn(self, items):
        return None

    def apply_correction(self, correction, exercise):
        return None

    def answer(self, word, sentence):
        return {"sense": HOLD, "provenance": []}

    def retrieve(self, **query):
        return []

    def history(self, word, sense):
        return []

    def save(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "student_state.json").write_text(json.dumps({"kind": "EmptyStudent"}), encoding="utf-8")

    @classmethod
    def load(cls, directory):
        return cls()
