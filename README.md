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

## 🛠️ Architecture

```
                      ┌───────────────┐
                      │    User CV    │
                      └───────┬───────┘
                              ▼
                      ┌───────────────┐
                      │   LLM Agent   │
                      └───────┬───────┘
                              ▼ (Extracted Skills/Interests)
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       ┌───────────┐    ┌───────────┐    ┌───────────┐
       │   Neo4j   │    │  Qdrant   │    │   Rust    │
       │ (Graph)   │    │ (Vector)  │    │ (Scoring) │
       └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                      ┌───────────────┐
                      │  Ranked Orgs  │
                      └───────┬───────┘
                              ▼
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Interactive │      │      CV      │      │   Proposal   │
│  Graph UI    │      │  Roadmaps    │      │   Drafts     │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 📦 Project Structure

```text
GSoCPathfinder/
├── Data/                   # 11 years of GSoC JSON datasets (2016–2026)
├── rust_engine/            # High-performance Rust scoring crate (PyO3)
│   ├── src/lib.rs          # Jaccard and scoring algorithms
│   ├── Cargo.toml          # Rust dependencies
│   └── pyproject.toml      # Maturin build settings
├── frontend/               # React / Vite Single Page Application
│   ├── src/
│   │   ├── components/     # UI elements (GraphViz, ChatWidget, OrgCard, CVInput)
│   │   ├── App.jsx         # App container and theme provider
│   │   └── index.css       # Core typography (Roboto Mono)
│   ├── package.json        # Frontend configuration
│   └── vite.config.js      # Dev server settings
├── src/                    # Backend API and Agent Workflows
│   ├── agent/              # LangGraph orchestration state & nodes
│   ├── api/                # FastAPI endpoints (matching, chat, proposal, roadmap)
│   ├── config/             # YAML configurations (weights, synonyms, settings)
│   ├── graph/              # Neo4j Client connections and schemas
│   ├── vector/             # Qdrant Client connections and collections
│   ├── scoring/            # Scoring rankers and weights loading
│   ├── llm/                # OpenAI/Local LM Studio client wrappers
│   └── models.py           # Pydantic schemas
├── scripts/                # CLI runners (ingestion, validation, match tests)
├── docker-compose.yml      # DB services (Neo4j Community + Qdrant)
└── pyproject.toml          # uv backend settings
```

---

## 🚦 Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **[uv](https://docs.astral.sh/uv/)** (Python environment manager)
- **Rust toolchain** (for compiling the scoring engine)
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

---

## 📄 License

MIT

