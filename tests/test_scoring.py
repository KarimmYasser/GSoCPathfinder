import pytest

try:
    import pathfinder_rs
except ImportError:
    # Fallback/mock for environments where maturin hasn't compiled yet
    pathfinder_rs = None

def test_jaccard_overlap_empty():
    if pathfinder_rs is None:
        pytest.skip("rust_engine not compiled")
    
    score = pathfinder_rs.f1_skill_overlap([], ["python"], "")
    assert score == 0.0

def test_jaccard_overlap_exact_match():
    if pathfinder_rs is None:
        pytest.skip("rust_engine not compiled")
        
    score = pathfinder_rs.f1_skill_overlap(["python", "rust"], ["python", "rust"], "")
    assert score == 1.0

def test_jaccard_overlap_partial_match():
    if pathfinder_rs is None:
        pytest.skip("rust_engine not compiled")
        
    # intersection: python (weight 1.0)
    # union: python, rust, go (weight 1.0 + 1.0 + 1.0 = 3.0)
    # score: 1/3
    score = pathfinder_rs.f1_skill_overlap(["python", "rust"], ["python", "go"], "")
    assert pytest.approx(score) == 0.3333333333333333

def test_jaccard_overlap_weighted():
    if pathfinder_rs is None:
        pytest.skip("rust_engine not compiled")
        
    # "python" appears twice -> weight 2.0
    # "rust" is not in CV text -> weight 1.0
    # "go" is not in cv_set -> weight 1.0
    # intersection: python (weight 2.0)
    # union: python (weight 2.0), rust (weight 1.0), go (weight 1.0) -> union_weight = 4.0
    # score: 2.0 / 4.0 = 0.5
    score = pathfinder_rs.f1_skill_overlap(
        ["python", "rust"], 
        ["python", "go"], 
        "I love Python. Python is great."
    )
    assert score == 0.5
