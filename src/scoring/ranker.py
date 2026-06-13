"""Combines all signals, calculates scores, and ranks organizations."""

from datetime import datetime
from models import UserProfile, RankedOrganization, ScoreBreakdown
from scoring.factors import ScoringFactors
from scoring.weights import load_weights

class MatchingEngine:
    """Combines graph and vector signals to rank organizations."""
    
    def __init__(self):
        self.weights = load_weights()
        self.current_year = datetime.now().year
        # In our dataset, the max year is 2026
        # To be safe, we'll bound the current year for calculations 
        # so recency doesn't break if run in e.g. 2030 without new data
        if self.current_year > 2026:
            self.current_year = 2026

    def rank_organizations(
        self, 
        user_profile: UserProfile, 
        vector_results: list[dict], 
        graph_results: list[dict]
    ) -> list[RankedOrganization]:
        """Merge results and calculate final rankings."""
        
        # Merge by canonical_name
        orgs_map = {}
        
        # 1. Process Vector Results
        for vr in vector_results:
            name = vr["canonical_name"]
            orgs_map[name] = {
                "canonical_name": name,
                "description": vr.get("description", ""),
                "url": vr.get("url", ""),
                "years_active": vr.get("years_active", []),
                "technologies": vr.get("technologies", []),
                "topics": vr.get("topics", []),
                "total_projects": vr.get("total_projects", 0),
                "qdrant_score": vr.get("similarity_score", 0.0),
                "matched_skills": [] # will be populated from graph if available
            }
            
        # 2. Process Graph Results
        for gr in graph_results:
            name = gr["canonical_name"]
            if name not in orgs_map:
                # If it wasn't found by semantic search, we need to fetch its full details
                # In a real pipeline, the graph query should return these, or we do a lookup.
                # For now, we use what the graph returned.
                orgs_map[name] = {
                    "canonical_name": name,
                    "description": gr.get("description", ""),
                    "years_active": gr.get("years_active", []),
                    "matched_skills": gr.get("matched_skills", []),
                    "technologies": gr.get("matched_skills", []), # approx fallback
                    "topics": [],
                    "total_projects": 0,
                    "qdrant_score": 0.0
                }
            else:
                orgs_map[name]["matched_skills"] = gr.get("matched_skills", [])
                
        # 3. Calculate Scores
        ranked_orgs = []
        for name, data in orgs_map.items():
            breakdown = ScoreBreakdown()
            
            # f1: Skill Overlap
            breakdown.skill_overlap = ScoringFactors.f1_skill_overlap(
                user_profile.skills, data["technologies"], user_profile.raw_cv_text
            )
            
            # f2: Semantic Similarity
            breakdown.semantic_similarity = ScoringFactors.f2_semantic_similarity(
                data["qdrant_score"]
            )
            
            # f3: Recency + Frequency
            breakdown.recency_frequency = ScoringFactors.f3_recency_frequency(
                data["years_active"], self.current_year, self.weights
            )
            
            # f4: Topic Alignment
            breakdown.topic_alignment = ScoringFactors.f4_topic_alignment(
                user_profile.topics_of_interest, data["topics"]
            )
            
            # f5: Project Volume
            breakdown.project_volume = ScoringFactors.f5_project_volume(
                data["total_projects"], len(data["years_active"]), self.weights
            )
            
            # f6: Org Stability
            breakdown.org_stability = ScoringFactors.f6_org_stability(
                data["years_active"], self.current_year, self.weights
            )
            
            # Calculate Total Score
            breakdown.total = (
                (breakdown.skill_overlap * self.weights.skill_overlap) +
                (breakdown.semantic_similarity * self.weights.semantic_similarity) +
                (breakdown.recency_frequency * self.weights.recency_frequency) +
                (breakdown.topic_alignment * self.weights.topic_alignment) +
                (breakdown.project_volume * self.weights.project_volume) +
                (breakdown.org_stability * self.weights.org_stability)
                # LLM relevance is added later by the LLM evaluation node
            )
            
            org = RankedOrganization(
                rank=0, # Assigned after sorting
                canonical_name=name,
                description=data["description"],
                url=data.get("url", ""),
                category="", # Could be added
                years_active=sorted(data["years_active"]),
                matched_technologies=data["matched_skills"],
                matched_topics=list(set(user_profile.topics_of_interest).intersection(
                    set(t.lower() for t in data["topics"])
                )),
                score=breakdown
            )
            ranked_orgs.append(org)
            
        # 4. Sort and assign ranks
        ranked_orgs.sort(key=lambda x: x.score.total, reverse=True)
        for i, org in enumerate(ranked_orgs):
            org.rank = i + 1
            
        return ranked_orgs
