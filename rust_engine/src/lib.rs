use pyo3::prelude::*;
use std::collections::HashSet;

/// Factor 1: Weighted Jaccard similarity between CV skills and org technologies.
#[pyfunction]
#[pyo3(signature = (user_skills, org_technologies, raw_cv_text="".to_string()))]
fn f1_skill_overlap(user_skills: Vec<String>, org_technologies: Vec<String>, raw_cv_text: String) -> f64 {
    let raw_lower = raw_cv_text.to_lowercase();
    
    let mut cv_set = HashSet::new();
    for s in user_skills {
        cv_set.insert(s.to_lowercase());
    }
    
    let mut org_set = HashSet::new();
    for t in org_technologies {
        org_set.insert(t.to_lowercase());
    }
    
    if cv_set.is_empty() || org_set.is_empty() {
        return 0.0;
    }
    
    let get_weight = |skill: &str| -> f64 {
        let count = raw_lower.matches(skill).count();
        if count == 0 { 1.0 } else { count as f64 }
    };
    
    let mut intersection_weight = 0.0;
    for skill in cv_set.intersection(&org_set) {
        intersection_weight += get_weight(skill);
    }
    
    let mut union_weight = 0.0;
    let union_set: HashSet<_> = cv_set.union(&org_set).collect();
    for skill in union_set {
        if cv_set.contains(skill) {
            union_weight += get_weight(skill);
        } else {
            union_weight += 1.0;
        }
    }
    
    if union_weight > 0.0 {
        intersection_weight / union_weight
    } else {
        0.0
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn pathfinder_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(f1_skill_overlap, m)?)?;
    Ok(())
}
