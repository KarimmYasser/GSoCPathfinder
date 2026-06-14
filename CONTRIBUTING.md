# Contributing to GSoC Pathfinder 🧭

Thank you for your interest in contributing to GSoC Pathfinder! We welcome and appreciate contributions of all kinds, whether it's fixing bugs, adding new features, improving documentation, or offering feedback.

To ensure a smooth collaboration, please review the following guidelines.

---

## 🛠️ Local Development Setup

To get started, make sure you have the following prerequisites installed on your system:
- **Python 3.12+**
- **Node.js 18+** (with npm)
- **Rust toolchain** (cargo/rustc) - for compiling the high-performance scoring engine.
- **Docker & Docker Compose** - to run Neo4j and Qdrant.
- **[uv](https://docs.astral.sh/uv/)** (Python environment and package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/KarimmYasser/GSoCPathfinder.git
cd GSoCPathfinder
```

### 2. Start Local Databases

Start the Neo4j and Qdrant database containers in the background:
```bash
docker compose up -d
```

### 3. Configure the Environment

Copy the example environment file and configure it:
```bash
cp .env.example .env
```
Ensure you have configured either a local LLM server (like LM Studio or Ollama) or set up remote API access.

### 4. Setup Python Environment and Compile Rust Engine

GSoC Pathfinder uses `uv` for workspace dependency management. Sync dependencies and build the Rust engine in-place:
```bash
uv sync
```
This builds and installs the `rust_engine` module as a local workspace dependency.

### 5. Ingest Historical Data

Run the ingestion scripts to download/preprocess historical GSoC data and load them into Neo4j and Qdrant:
```bash
uv run python scripts/ingest.py
```

### 6. Start the Backend API Server

Launch the FastAPI development server:
```bash
uv run uvicorn src.api.server:app --reload --port 8000
```

### 7. Start the Frontend App

Navigate to the frontend folder, install dependencies, and run the Vite server:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🤝 How to Contribute

### 1. Find or Report an Issue
- Look through our [Issue Tracker](https://github.com/KarimmYasser/GSoCPathfinder/issues) for issues labeled `good first issue` or `help wanted`.
- If you find a bug or want to suggest a feature, please create a new issue using the provided templates.

### 2. Standard Branching & Workflow
1. **Fork** the repository and clone it locally.
2. Create a new branch off `main` for your work. Use descriptive names:
   - `feat/your-feature-name`
   - `fix/bug-description`
   - `docs/what-you-documented`
   - `chore/upgrade-deps`
3. Write clean, well-commented code. Keep existing comments and docstrings unless they need updates.
4. Add tests for new functionality under the `tests/` directory.
5. Run existing tests to ensure no regressions:
   ```bash
   uv run pytest
   ```
6. Format and lint your changes:
   - **Python**: Run `uv run ruff check` and `uv run ruff format`
   - **Rust**: Run `cargo fmt` inside `rust_engine/`
   - **Frontend**: Run `npm run lint` inside `frontend/`

### 3. Commit Guidelines (Conventional Commits)
Please format your commit messages using the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat: add CV parser node to LangGraph pipeline`
- `fix: resolve Jaccard division by zero error in Rust engine`
- `docs: update setup steps in CONTRIBUTING.md`
- `style: fix alignment on organization cards`

### 4. Submit a Pull Request
1. Push your branch to your fork.
2. Open a Pull Request (PR) against our `main` branch.
3. Fill out the **PR template** thoroughly, linking the related issue and detailing how you tested your changes.
4. Ensure the CI suite checks pass successfully.

---

## ⚖️ Code of Conduct
All contributors are expected to uphold the [Code of Conduct](file:///d:/Projects/GSoCPathfinder/CODE_OF_CONDUCT.md). Please report any unacceptable behavior to `karimmyasserr@gmail.com`.
