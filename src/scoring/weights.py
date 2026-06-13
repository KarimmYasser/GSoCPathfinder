"""Weight configuration loader for the scoring engine."""

import yaml
from pathlib import Path
from pydantic import BaseModel

class RecencyWeights(BaseModel):
    recency_weight: float = 0.6
    consistency_weight: float = 0.4

class StabilityParams(BaseModel):
    avg_project_cap: float = 10.0
    recent_window: int = 3
    inactive_penalty: float = 0.20

class ScoringWeights(BaseModel):
    skill_overlap: float = 0.25
    semantic_similarity: float = 0.20
    recency_frequency: float = 0.20
    topic_alignment: float = 0.10
    project_volume: float = 0.10
    org_stability: float = 0.10
    llm_relevance: float = 0.05
    
    recency: RecencyWeights = RecencyWeights()
    stability: StabilityParams = StabilityParams()
    
    def validate_weights(self):
        """Ensure base weights sum to 1.0 (with small float tolerance)."""
        total = sum([
            self.skill_overlap, self.semantic_similarity, 
            self.recency_frequency, self.topic_alignment,
            self.project_volume, self.org_stability, self.llm_relevance
        ])
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total}")

def load_weights(config_path: Path | str | None = None) -> ScoringWeights:
    """Load weights from YAML or return defaults."""
    if not config_path:
        # Default to src/config/weights.yaml
        config_path = Path(__file__).parent.parent / "config" / "weights.yaml"
        
    path = Path(config_path)
    if not path.exists():
        print(f"Warning: {path} not found. Using default weights.")
        return ScoringWeights()
        
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    if not data:
        return ScoringWeights()
        
    # Build models
    weights = ScoringWeights(**data.get("weights", {}))
    weights.recency = RecencyWeights(**data.get("recency", {}))
    weights.stability = StabilityParams(**data.get("stability", {}))
    
    weights.validate_weights()
    return weights
