"""FastAPI server for the GSoC Pathfinder matching engine."""
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to Python path to allow imports like 'from agent...'
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.workflow import create_matching_workflow
from agent.state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GSoC Pathfinder API",
    description="API for matching student CVs to GSoC organizations.",
    version="0.1.0",
)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    cv_text: str

@app.post("/api/match")
async def match_cv(request: MatchRequest) -> Dict[str, Any]:
    """Run the matching workflow for the provided CV text."""
    if not request.cv_text or not request.cv_text.strip():
        raise HTTPException(status_code=400, detail="CV text cannot be empty.")

    logger.info("Received matching request for CV (length: %d)", len(request.cv_text))
    
    try:
        # Create and invoke the workflow
        workflow = create_matching_workflow()
        
        # Initialize state exactly matching AgentState
        initial_state = AgentState(
            raw_cv_text=request.cv_text,
            user_profile=None,
            graph_results=[],
            vector_results=[],
            ranked_organizations=[],
            match_result=None
        )
        
        logger.info("Starting workflow execution...")
        # Invoke LangGraph (it handles the async nodes internally)
        final_state = await workflow.ainvoke(initial_state)
        
        # Extract the final MatchResult dict
        match_data = final_state.get("match_result")
        
        if not match_data:
            raise HTTPException(status_code=500, detail="Workflow completed but returned no results.")
            
        logger.info("Workflow complete. Returning %d rankings.", len(match_data.get("rankings", [])))
        return match_data
        
    except Exception as e:
        logger.error("Error during matching workflow: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

class IssuesRequest(BaseModel):
    url: str

@app.post("/api/issues")
async def get_issues(request: IssuesRequest):
    """Fetch Good First Issues for a given organization repository URL."""
    from api.github import fetch_good_first_issues
    issues = await fetch_good_first_issues(request.url)
    return {"issues": [i.dict() for i in issues]}

from api.chat import ChatRequest, handle_chat

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle interactive chat with context."""
    try:
        reply = await handle_chat(request)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProposalRequest(BaseModel):
    cv_text: str
    org_name: str
    org_desc: str

@app.post("/api/proposal")
async def draft_proposal(request: ProposalRequest):
    """Generate a GSoC proposal draft."""
    from agent.proposal_generator import generate_proposal
    try:
        proposal = await generate_proposal(request.cv_text, request.org_name, request.org_desc)
        return {"proposal": proposal}
    except Exception as e:
        logger.error(f"Proposal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class GraphRequest(BaseModel):
    skills: list[str]
    org_names: list[str]

@app.post("/api/graph_data")
async def get_graph(request: GraphRequest):
    """Fetch Knowledge Graph data for visualization."""
    from api.graph import get_knowledge_graph
    try:
        data = await get_knowledge_graph(request.skills, request.org_names)
        return data
    except Exception as e:
        logger.error(f"Graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class OptimizeRequest(BaseModel):
    cv_text: str
    org_name: str
    org_desc: str

@app.post("/api/optimize_cv")
async def draft_optimization(request: OptimizeRequest):
    """Generate a learning roadmap."""
    from agent.cv_optimizer import optimize_cv
    try:
        roadmap = await optimize_cv(request.cv_text, request.org_name, request.org_desc)
        return {"roadmap": roadmap}
    except Exception as e:
        logger.error(f"Optimizer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

