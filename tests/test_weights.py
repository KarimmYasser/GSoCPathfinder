"""Tests for scoring weights loading."""

import pytest

from scoring.weights import ScoringWeights, load_weights


def test_load_weights_returns_valid_instance():
    weights = load_weights()
    assert isinstance(weights, ScoringWeights)


def test_weights_sum_to_one():
    weights = load_weights()
    total = (
        weights.skill_overlap
        + weights.semantic_similarity
        + weights.recency_frequency
        + weights.topic_alignment
        + weights.project_volume
        + weights.org_stability
        + weights.llm_relevance
    )
    assert pytest.approx(total) == 1.0


def test_weights_are_positive():
    weights = load_weights()
    assert weights.skill_overlap > 0
    assert weights.semantic_similarity > 0
    assert weights.topic_alignment > 0
    assert weights.org_stability > 0
    assert weights.llm_relevance > 0


def test_recency_weights_sum():
    weights = load_weights()
    total = weights.recency.recency_weight + weights.recency.consistency_weight
    assert pytest.approx(total) == 1.0
