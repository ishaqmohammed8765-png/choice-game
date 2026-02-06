"""Shared test configuration."""

from game.data import init_story_nodes


def pytest_configure(config):
    """Ensure story simplification runs once before any tests."""
    init_story_nodes()
