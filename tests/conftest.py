"""Shared test fixtures for GSoC Pathfinder tests."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_user_skills():
    return ["python", "rust", "javascript"]


@pytest.fixture
def sample_org_technologies():
    return ["python", "go", "rust"]


@pytest.fixture
def sample_cv_text():
    return (
        "I am a software engineer with 3 years of experience in Python and Rust. "
        "I have built web applications using JavaScript and React. "
        "I am interested in machine learning, open source, and distributed systems."
    )


@pytest.fixture
def sample_years_active():
    return [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]


@pytest.fixture
def sample_user_topics():
    return ["machine learning", "open source", "distributed systems"]


@pytest.fixture
def sample_org_topics():
    return ["open source", "web development", "machine learning"]
