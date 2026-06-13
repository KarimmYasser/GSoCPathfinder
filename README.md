# GSoC Pathfinder 🧭

**AI-powered Google Summer of Code organization matching engine, CV optimizer, and visualization dashboard.**

GSoC Pathfinder helps aspiring students find the best Google Summer of Code organizations for their profile. By leveraging a high-performance Rust scoring engine, a Neo4j knowledge graph, a Qdrant semantic vector database, and LangGraph AI agents, it maps out the GSoC ecosystem to match skills, analyze learning gaps, draft proposals, and visualize connections.

---

## 🚀 Key Features

1. **Ingest & Normalize:** Parses 11 years of historical GSoC data (2016–2026), cleaning HTML and canonicalizing 663 organizations and 12,000+ projects using YAML synonym maps.
2. **Dual-Database Knowledge Retrieval:**
   - **Neo4j Graph Database:** Captures temporal organization profiles, category groupings, and technology relationships.
   - **Qdrant Vector Store:** Index project descriptions using semantic embeddings for advanced matching.
3. **High-Performance Rust Scoring Engine:** Scoring math is offloaded to a core Rust module bound to Python via **PyO3/Maturin** for fast parallel calculations.
4. **7-Factor Ranking System:** Ranks organizations based on Skill Overlap (25%), Semantic Similarity (15%), Recency & Frequency (15%), Topic Alignment (10%), Project Volume (10%), Org Stability (10%), and LLM Relevance (15%).
5. **Interactive UI Dashboard (Google Material Design):**
   - **Responsive Grid:** Sleek dashboard with animations and curated Google theme elevations.
   - **Knowledge Graph Visualizer:** Fully interactive 2D force-directed graph featuring hover-active highlights, connection flows, smart label visibility, and zoom controls.
   - **CV Learning Roadmap Optimizer:** Generates a custom gap analysis and learning roadmap of exactly what skills to learn for any target organization.
   - **Proposal Draft Generator:** Drafts customized GSoC proposals tailored to your CV and the organization's past projects.
   - **Match Chat Assistant:** A draggable, resizable, and minimizable chat widget rendering native Markdown to discuss matched organizations in real-time.
   - **GitHub Good First Issues:** Fetches recruiting organization repositories and actively pulls beginner-friendly issues.

---

## 🧠 Core Architecture

### LangGraph Agent Workflow
The matching engine runs on a structured **LangGraph** execution pipeline:

```text
                  ┌───────────────────────┐
                  │         START         │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │       extractor       │ (Extracts profile from CV text)
                  └───────────┬───────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼ (Parallel Search)           ▼ (Parallel Search)
   ┌───────────────────────┐     ┌───────────────────────┐
   │     graph_querier     │     │    vector_searcher    │
   │ (Queries Neo4j Graph) │     │ (Queries Qdrant Vect) │
   └───────────┬───────────┘     └───────────┬───────────┘
               │                             │
               └──────────────┬──────────────┘
                              │ (Fan-In Join)
                              ▼
                  ┌───────────────────────┐
                  │        merger         │ (Merges & applies scoring formula)
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │       explainer       │ (Generates LLM justifications)
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │          END          │
                  └───────────────────────┘
```

1. **`extractor`**: Extracts structured profile data (programming languages, frameworks, interests) from the user's raw CV text using LLM function calling.
2. **`graph_querier`**: Queries Neo4j for organizations matching extracted technologies and topics.
3. **`vector_searcher`**: Embeds the CV text and queries Qdrant for semantically relevant historical GSoC projects.
4. **`merger`**: Combines vector and graph records, executing scoring functions (including the Rust Jaccard module) to compute rank scores.
5. **`explainer`**: Uses the LLM to generate narrative matching explanations for the top matched organizations.

### Rust Scoring Engine (`rust_engine`)
The weighted Jaccard similarity score (Factor 1: Skill Overlap) is compiled to binary machine code in Rust for performance:
* **F1 Algorithm:** Computes Jaccard index based on the intersection and union of CV skills and organization technologies.
* **CV Frequency Weighting:** Searches the raw CV text for each matching skill. Skills that appear more frequently in the user's CV carry higher weights during the Jaccard intersection calculation to favor core strengths.

---

## 💾 Database Schemas

### 1. Neo4j Graph Schema
Neo4j models the GSoC network across years with the following nodes and relationships:
* **Nodes:**
  - `(o:Organization)` - Canonical GSoC organization details.
  - `(p:Project)` - Historical accepted GSoC projects.
  - `(t:Technology)` - Programming languages, libraries, and frameworks.
  - `(tp:Topic)` - Domain categories (e.g., machine learning, security, web).
  - `(y:YearProfile)` - An organization's specific participation profile for a single GSoC year.
* **Relationships:**
  - `(o)-[:HAS_PROFILE]->(y)`
  - `(y)-[:USES]->(t)`
  - `(y)-[:FOCUSES_ON]->(tp)`
  - `(y)-[:ACCEPTED_PROJECT]->(p)`

### 2. Qdrant Vector Payload
The `gsoc_projects` collection indexes historical projects. Each vector has the following metadata payload:
```json
{
  "project_title": "string",
  "project_description": "string",
  "org_canonical_name": "string",
  "year": 2024,
  "technologies": ["string"],
  "topics": ["string"]
}
```

---

## 📡 REST API Specifications

The FastAPI backend exposes the following endpoints:

### 1. Match CV
* **Endpoint:** `POST /api/match`
* **Request Payload:**
  ```json
  { "cv_text": "Full text content of the user's CV/resume..." }
  ```
* **Response:**
  Returns a `MatchResult` schema containing the extracted `user_profile` and a list of `RankedOrganization` objects, each with detailed sub-score breakdown (Skill overlap, semantic match, stability, etc.) and LLM explanation text.

### 2. Match Assistant Chat
* **Endpoint:** `POST /api/chat`
* **Request Payload:**
  ```json
  {
    "messages": [
      { "role": "user", "content": "Tell me more about their machine learning projects." }
    ],
    "context": [ ...list of matched organizations... ]
  }
  ```
* **Response:**
  ```json
  { "reply": "LLM assistant response formatted in Markdown..." }
  ```

### 3. Draft Proposal
* **Endpoint:** `POST /api/proposal`
* **Request Payload:**
  ```json
  {
    "cv_text": "User CV text...",
    "org_name": "Python Software Foundation",
    "org_desc": "Organization description..."
  }
  ```
* **Response:**
  ```json
  { "proposal": "Custom GSoC proposal draft (Markdown)..." }
  ```

### 4. Optimize CV (Learning Roadmap)
* **Endpoint:** `POST /api/optimize_cv`
* **Request Payload:**
  Same as `/api/proposal`.
* **Response:**
  ```json
  { "roadmap": "Gap analysis and learning timeline roadmap..." }
  ```

### 5. Fetch Graph Data
* **Endpoint:** `POST /api/graph_data`
* **Request Payload:**
  ```json
  {
    "skills": ["python", "go", "react"],
    "org_names": ["Kubeflow", "SCoRe Lab"]
  }
  ```
* **Response:**
  Returns a JSON graph structure (`{ "nodes": [...], "links": [...] }`) mapping connections between the user, their skills, organizations, and their technologies.

### 6. GitHub Good First Issues
* **Endpoint:** `POST /api/issues`
* **Request Payload:**
  ```json
  { "url": "https://github.com/org/repo" }
  ```
* **Response:**
  List of beginners' GitHub issues fetched dynamically using GitHub APIs.

---

## ⚙️ Environment Variables

Configure the following variables in your `.env` file:

```ini
# === LLM Provider Configuration ===
LLM_PROVIDER=local                          # "local" (LM Studio/Ollama) or "remote" (OpenAI)

# Chat Model Settings
LLM_BASE_URL=http://localhost:1234/v1       # Endpoint of local provider or OpenAI URL
LLM_API_KEY=lm-studio                       # API Key (use "lm-studio" for local dev, or OpenAI Key)
LLM_CHAT_MODEL=your-chat-model-name         # Model ID to use for chat, roadmaps, and proposals

# Embedding Model Settings
EMBED_BASE_URL=http://localhost:1234/v1     # Endpoint of embedding provider
EMBED_API_KEY=lm-studio                     # API Key for embedding service
EMBED_MODEL=your-embed-model-name           # Embedding Model ID
EMBED_DIMENSION=768                         # Match the dimension size of the embedding model

# === Neo4j Graph Settings ===
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=pathfinder123

# === Qdrant Vector Settings ===
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# === Local Data Settings ===
DATA_DIR=./Data
TOP_N_RESULTS=10                            # Number of organization matches to return
EMBED_BATCH_SIZE=32                         # Ingestion embedding batch sizes
```

---

## 🚦 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **[uv](https://docs.astral.sh/uv/)** (Python environment manager)
- **Rust toolchain** (to build the scoring engine)
- **LM Studio** (running local chat/embedding models) or an **OpenAI API Key**

### 1. Database & Environment Setup
Start the Neo4j and Qdrant database containers:
```bash
docker compose up -d
```
Copy the environment template and fill in your LLM API parameters:
```bash
cp .env.example .env
```

### 2. Ingest Historical Data
Sync workspace dependencies and compile the Rust scoring library:
```bash
# This syncs dependencies and builds the rust_engine in-place
uv sync
```
Ingest the historical GSoC data files:
```bash
uv run python scripts/ingest.py
```

### 3. Run the Backend API Server
Launch the FastAPI development server:
```bash
uv run uvicorn src.api.server:app --reload --port 8000
```

### 4. Run the Frontend Dashboard
Open a new terminal window, install npm packages, and start the Vite dev server:
```bash
cd frontend
npm install
npm run dev
```

Visit the dashboard in your browser at `http://localhost:5173`. Paste your CV, generate matches, explore the Knowledge Graph connections, optimization roadmap, beginner GitHub issues, and chat about your opportunities!

## 💡 Implementation Notes

* **Checking Recent Changes:** To see the exact code modifications made to the scoring engine, dynamic UI color coding, or auto-scrolling log features, use `git log`:
  ```bash
  git log -p -n 1
  ```

---

## 📄 License

MIT


