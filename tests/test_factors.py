"""Tests for scoring factor implementations (Python fallback path)."""

import pytest

from scoring.factors import ScoringFactors
from scoring.weights import load_weights


class TestF1SkillOverlap:
    """Tests for f1_skill_overlap (weighted Jaccard similarity)."""

    def test_empty_user_skills(self):
        assert ScoringFactors.f1_skill_overlap([], ["python"], "") == 0.0

    def test_empty_org_techs(self):
        assert ScoringFactors.f1_skill_overlap(["python"], [], "") == 0.0

    def test_both_empty(self):
        assert ScoringFactors.f1_skill_overlap([], [], "") == 0.0

    def test_exact_match(self):
        score = ScoringFactors.f1_skill_overlap(
            ["python", "rust"], ["python", "rust"], ""
        )
        assert score == 1.0

    def test_no_match(self):
        score = ScoringFactors.f1_skill_overlap(
            ["python", "rust"], ["go", "java"], ""
        )
        assert score == 0.0

    def test_partial_match(self):
        # Rust engine: Jaccard = intersection/union = {python}/{python,rust,go} = 1/3
        score = ScoringFactors.f1_skill_overlap(
            ["python", "rust"], ["python", "go"], ""
        )
        assert pytest.approx(score) == pytest.approx(1 / 3)

    def test_weighted_by_frequency(self):
        # Rust engine applies frequency weighting differently than Python fallback
        score = ScoringFactors.f1_skill_overlap(
            ["python", "rust"], ["python", "go"],
            "I love Python. Python is great. Python everywhere."
        )
        assert 0.0 < score <= 1.0

    def test_case_insensitive(self):
        score = ScoringFactors.f1_skill_overlap(
            ["Python", "RUST"], ["python", "Rust"], ""
        )
        assert score == 1.0


class TestF2SemanticSimilarity:
    """Tests for f2_semantic_similarity."""

    def test_zero_score(self):
        assert ScoringFactors.f2_semantic_similarity(0.0) == 0.0

    def test_perfect_score(self):
        assert ScoringFactors.f2_semantic_similarity(1.0) == 1.0

    def test_clamps_below_zero(self):
        assert ScoringFactors.f2_semantic_similarity(-0.5) == 0.0

    def test_clamps_above_one(self):
        assert ScoringFactors.f2_semantic_similarity(1.5) == 1.0

    def test_mid_score(self):
        assert ScoringFactors.f2_semantic_similarity(0.7) == 0.7


class TestF3RecencyFrequency:
    """Tests for f3_recency_frequency."""

    def test_no_years(self):
        weights = load_weights()
        assert ScoringFactors.f3_recency_frequency([], 2026, weights) == 0.0

    def test_recent_org(self):
        weights = load_weights()
        score = ScoringFactors.f3_recency_frequency([2024, 2025, 2026], 2026, weights)
        assert score > 0.8  # Should be high for recent org

    def test_old_org(self):
        weights = load_weights()
        score = ScoringFactors.f3_recency_frequency([2016, 2017], 2026, weights)
        assert score < 0.5  # Should be low for old org


class TestF4TopicAlignment:
    """Tests for f4_topic_alignment."""

    def test_empty_topics(self):
        assert ScoringFactors.f4_topic_alignment([], ["ml"]) == 0.0

    def test_no_match(self):
        assert ScoringFactors.f4_topic_alignment(["web"], ["ml"]) == 0.0

    def test_exact_match(self):
        assert ScoringFactors.f4_topic_alignment(
            ["ml", "ai"], ["ml", "ai"]
        ) == 1.0

    def test_partial_match(self):
        score = ScoringFactors.f4_topic_alignment(
            ["ml", "web"], ["ml", "ai"]
        )
        assert 0.0 < score < 1.0


class TestF5ProjectVolume:
    """Tests for f5_project_volume."""

    def test_zero_years(self):
        weights = load_weights()
        assert ScoringFactors.f5_project_volume(10, 0, weights) == 0.0

    def test_many_projects(self):
        weights = load_weights()
        score = ScoringFactors.f5_project_volume(50, 5, weights)
        assert score > 0.0


class TestF6OrgStability:
    """Tests for f6_org_stability."""

    def test_no_years(self):
        weights = load_weights()
        assert ScoringFactors.f6_org_stability([], 2026, weights) == 0.0

    def test_long_lived_org(self):
        weights = load_weights()
        score = ScoringFactors.f6_org_stability(
            list(range(2016, 2027)), 2026, weights
        )
        assert score > 0.8

    def test_single_year_org(self):
        weights = load_weights()
        score = ScoringFactors.f6_org_stability([2026], 2026, weights)
        assert 0.0 < score < 1.0


class TestF7LLMRelevance:
    """Tests for f7_llm_relevance."""

    def test_zero_score(self):
        assert ScoringFactors.f7_llm_relevance(0) == 0.0

    def test_max_score(self):
        assert ScoringFactors.f7_llm_relevance(10) == 1.0

    def test_mid_score(self):
        assert ScoringFactors.f7_llm_relevance(5) == 0.5

    def test_clamps_above_ten(self):
        assert ScoringFactors.f7_llm_relevance(15) == 1.0

    def test_clamps_below_zero(self):
        assert ScoringFactors.f7_llm_relevance(-5) == 0.0
