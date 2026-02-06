"""Streamlit import compatibility layer.

Uses real Streamlit when available. In test/offline contexts where Streamlit
is unavailable, provides a tiny stub with `session_state` so core logic can be
unit tested.
"""

from __future__ import annotations


class _SessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _FallbackStreamlit:
    def __init__(self) -> None:
        self.session_state = _SessionState()


try:  # pragma: no cover - exercised in real app runtime
    import streamlit as st  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised in tests
    st = _FallbackStreamlit()
