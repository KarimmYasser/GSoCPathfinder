# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-06-14

### Added
- **LangGraph Agent Workflow**: Pipeline including `extractor`, `graph_querier`, `vector_searcher`, `merger`, and `explainer`.
- **Dual-Database Support**: Integration with Neo4j graph database and Qdrant vector database.
- **Rust Scoring Engine**: High-performance scoring library bound to Python using PyO3/Maturin, implementing weighted Jaccard similarity.
- **Interactive UI Dashboard**: Responsive grid layout utilizing Material Design guidelines, complete with visualizers, CV optimization, matching chat assistant, proposal draft generator, and Good First Issues aggregator.
- **Ingestion & Normalization**: Data scripts to clean and ingest 11 years of GSoC history data.
- **Open Source Health Files**: MIT License, Code of Conduct, Security Policy, and Contributing Guidelines.
