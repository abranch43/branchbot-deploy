import os
import pytest

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv('SAM_API_KEY','dummy')
    monkeypatch.setenv('OPENAI_API_KEY','dummy')