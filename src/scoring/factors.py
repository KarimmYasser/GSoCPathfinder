"""The 7 scoring factors for matching a user CV to an organization."""

from scoring.weights import ScoringWeights


class ScoringFactors:
    """Implementations for all 7 scoring factors (f1 - f7)."""

    @staticmethod
    def f1_skill_overlap(
        user_skills: list[str], org_technologies: list[str], raw_cv_text: str = ""
    ) -> float:
        """
        Factor 1 (25%): Weighted Jaccard similarity between CV skills and org technologies.
        Skills mentioned more frequently in the raw CV text carry a higher weight.
        """
        try:
            import pathfinder_rs

            return pathfinder_rs.f1_skill_overlap(user_skills, org_technologies, raw_cv_text)
        except ImportError:
            cv_set = set(s.lower() for s in user_skills)
            org_set = set(t.lower() for t in org_technologies)

            if not cv_set or not org_set:
                return 0.0

            raw_text_lower = raw_cv_text.lower()

            def get_weight(skill: str) -> float:
                count = raw_text_lower.count(skill)
                return max(1, count)

            intersection = cv_set.intersection(org_set)

            # User-centric precision: what fraction of MY skills does this org cover?
            # Weighted by how prominently each skill appears in the CV.
            # This avoids penalizing orgs that have a broader tech stack (Jaccard's flaw).
            matched_weight = sum(get_weight(s) for s in intersection)
            total_cv_weight = sum(get_weight(s) for s in cv_set)

            return matched_weight / total_cv_weight if total_cv_weight > 0 else 0.0

    @staticmethod
    def f2_semantic_similarity(qdrant_score: float) -> float:
        """
        Factor 2 (20%): Cosine similarity from Qdrant vector search.
        Qdrant cosine similarity is already between 0.0 and 1.0 (if properly normalized).
        """
        # Ensure it's bounded
        return max(0.0, min(1.0, qdrant_score))

    @staticmethod
    def f3_recency_frequency(
        years_active: list[int], current_year: int, weights: ScoringWeights
    ) -> float:
        """
        Factor 3 (20%): How recently and consistently the org participates.
        """
        if not years_active:
            return 0.0

        # 1. Recency Score
        # Keep high score for recent ones (within last 3 years)
        most_recent = max(years_active)
        years_ago = current_year - most_recent

        if years_ago <= 3:
            recency_score = 1.0
        else:
            recency_score = max(0.0, 1.0 - (0.25 * (years_ago - 3)))

        # 2. Consistency Score (Fraction of total possible years they participated)
        # Total GSoC years in dataset = 11 (2016-2026)
        # We'll normalize against 10 years to give a slight boost to highly active orgs
        total_possible = 10.0
        consistency_score = min(1.0, len(years_active) / total_possible)

        rw = weights.recency
        return (recency_score * rw.recency_weight) + (consistency_score * rw.consistency_weight)

    @staticmethod
    def f4_topic_alignment(user_topics: list[str], org_topics: list[str]) -> float:
        """
        Factor 4 (10%): Jaccard similarity between CV interests and org topics.
        """
        cv_set = set(t.lower() for t in user_topics)
        org_set = set(t.lower() for t in org_topics)

        if not cv_set or not org_set:
            return 0.0

        intersection = len(cv_set.intersection(org_set))
        union = len(cv_set.union(org_set))

        # Topic matches are often sparse. If there's at least one match, we should
        # give a minimum baseline score (e.g., 0.5) to acknowledge the alignment.
        base_score = intersection / union
        if intersection > 0 and base_score < 0.5:
            # Boost sparse matches slightly
            return min(1.0, base_score * 1.5)

        return base_score

    @staticmethod
    def f5_project_volume(total_projects: int, years_active: int, weights: ScoringWeights) -> float:
        """
        Factor 5 (10%): Average number of projects per year (normalized).
        More projects = higher chance of acceptance.
        """
        if years_active == 0:
            return 0.0

        avg_per_year = total_projects / years_active
        cap = weights.stability.avg_project_cap

        return min(1.0, avg_per_year / cap)

    @staticmethod
    def f6_org_stability(
        years_active: list[int], current_year: int, weights: ScoringWeights
    ) -> float:
        """
        Factor 6 (10%): Org stability (longevity and recent activity).
        """
        if not years_active:
            return 0.0

        # 1. Longevity (difference between first and last year)
        first_year = min(years_active)
        last_year = max(years_active)
        longevity = last_year - first_year + 1  # 1 if single year
        longevity_score = min(1.0, longevity / 5.0)  # Caps at 5 years span

        # 2. Activity Check (did they participate in the last N years?)
        window = weights.stability.recent_window
        recent_activity = any((current_year - y) <= window for y in years_active)

        score = longevity_score
        if not recent_activity:
            score *= 1.0 - weights.stability.inactive_penalty

        return max(0.0, min(1.0, score))

    @staticmethod
    def f7_llm_relevance(llm_score: int) -> float:
        """
        Factor 7 (5%): LLM-generated relevance score [1-10] normalized to [0-1].
        """
        return max(0.0, min(1.0, llm_score / 10.0))
