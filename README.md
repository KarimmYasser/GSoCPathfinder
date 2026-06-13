# GSoC Pathfinder 🧭

**AI-powered Google Summer of Code organization matching engine.**

Find the best GSoC organizations for your skills, interests, and experience — powered by a knowledge graph, vector search, and LLM reasoning.

## What It Does

1. **Ingests** 11 years of GSoC data (2016–2026): 663 organizations, 12,095 projects
2. **Builds** a Neo4j knowledge graph with temporal organization profiles
3. **Embeds** organizations and projects into a Qdrant vector store
4. **Matches** your CV against the entire GSoC ecosystem using 7 scoring factors
5. **Explains** why each organization is a good fit, in natural language

## Architecture

```
CV Text ──► LLM (extract skills) ──┐
                                    ├──► Score & Rank ──► Explained Results
Neo4j (graph query) ───────────────┤
Qdrant (semantic search) ──────────┘
```

**Tech Stack**: Python 3.12+ · Neo4j · Qdrant · LangGraph · LM Studio / OpenAI

## Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- LM Studio (for local LLM) or an OpenAI API key

### Setup

```bash
# Clone and enter
cd GSoCPathfinder

# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your LLM settings

# Start Neo4j + Qdrant
docker compose up -d

# Ingest all data
uv run python scripts/ingest.py

# Match a CV
uv run python scripts/match.py --cv "paste your CV text here"
```

## Scoring Formula

Organizations are ranked using 7 weighted factors:

| Factor | Weight | Description |
|---|---|---|
| Skill Overlap | 25% | Jaccard similarity: your skills vs org's tech stack |
| Semantic Similarity | 20% | Embedding cosine similarity: your CV vs org profile |
| Recency + Frequency | 20% | How recently and consistently the org participates |
| Topic Alignment | 10% | Match between your interests and org's focus areas |
| Project Volume | 10% | Average projects per year (more slots = better odds) |
| Org Stability | 10% | Longevity, consistency, recent activity |
| LLM Relevance | 5% | AI-generated relevance assessment |

All weights are configurable in `src/config/weights.yaml`.

## Project Structure

```
GSoCPathfinder/
├── Data/               # 11 years of GSoC JSON data
├── src/
│   ├── config/         # Settings, weights, normalization maps
│   ├── ingestion/      # JSON parsing, normalization, loading
│   ├── graph/          # Neo4j knowledge graph
│   ├── vector/         # Qdrant vector store
│   ├── scoring/        # 7-factor scoring engine
│   ├── agent/          # LangGraph matching workflow
│   ├── llm/            # Unified LLM/embedding client
│   └── models.py       # Pydantic data models
├── scripts/            # CLI entry points
├── tests/              # Test suite
├── docker-compose.yml  # Neo4j + Qdrant containers
└── .env.example        # Environment template
```

## License

MIT
