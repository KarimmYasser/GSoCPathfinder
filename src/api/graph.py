from typing import List, Dict, Any
from graph.client import get_neo4j_client

async def get_knowledge_graph(skills: List[str], org_names: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch nodes and edges for the Knowledge Graph visualization."""
    client = await get_neo4j_client()
    
    # 1. Use provided CV skills
    cv_skills = set([s.lower() for s in skills])
    
    nodes = []
    links = []
    
    # Track node existence to prevent duplicates
    node_ids = set()
    
    def add_node(node_id: str, label: str, name: str):
        if node_id not in node_ids:
            nodes.append({"id": node_id, "name": name, "type": label})
            node_ids.add(node_id)
            
    def add_link(source: str, target: str):
        links.append({"source": source, "target": target})
        
    # Add User Node
    add_node("USER", "User", "My CV")
    
    # Add CV Skills
    for skill in cv_skills:
        skill_id = f"tech_{skill}"
        add_node(skill_id, "Skill", skill)
        add_link("USER", skill_id)

    if not org_names:
        return {"nodes": nodes, "links": links}
        
    # 2. Query Neo4j for Orgs and their Technologies
    query = """
    MATCH (o:Organization)
    WHERE o.canonical_name IN $org_names

    OPTIONAL MATCH (o)-[:HAS_PROFILE]->(:OrgProfile)-[:USES]->(ot:Technology)
    OPTIONAL MATCH (o)-[:OFFERS]->(:Project)-[:USES]->(pt:Technology)

    WITH o, collect(DISTINCT ot.name) + collect(DISTINCT pt.name) AS techs
    UNWIND techs AS tech

    WITH o, collect(DISTINCT tech) AS technologies

    RETURN
        o.canonical_name AS org_name,
        [t IN technologies WHERE t IS NOT NULL] AS technologies,
        size([t IN technologies WHERE t IS NOT NULL]) AS technology_count
    ORDER BY technology_count DESC
    """
    
    records = await client.execute_query(query, {"org_names": org_names})
    
    for record in records:
        org_name = record["org_name"]
        org_id = f"org_{org_name}"
        
        add_node(org_id, "Organization", org_name)
        
        techs = record["technologies"]
        for tech in techs:
            tech_lower = tech.lower()
            tech_id = f"tech_{tech_lower}"
            
            # If the tech is in CV skills, it will just reuse the node and link to it
            add_node(tech_id, "Technology", tech)
            add_link(org_id, tech_id)
            
    return {"nodes": nodes, "links": links}
