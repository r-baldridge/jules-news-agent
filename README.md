# Enterprise News Intelligence Agent (Local SLM Architecture)

## Executive Summary

The Enterprise News Intelligence Agent is an offline-capable, highly efficient extraction and orchestration engine. By shifting heavy lifting to deterministic algorithms (parsing, deduplication, and vetting) and reserving token-consuming Small Language Models (SLMs) exclusively for strict JSON knowledge extraction, the system transforms unstructured raw news into a verified, highly dense graph and vector knowledge base. This architecture drastically minimizes token overhead, ensures deterministic predictability, and guarantees "Zero-Hallucination" through strict source citations.

## Feature Index

1. **Deterministic Ingestion & Deduplication:** Python-native document routing with SHA-256 content hashing to ensure immutable storage and prevent duplicate processing.
2. **Strict SLM Knowledge Extraction:** Enforces JSON output using Pydantic schemas (Subject-Predicate-Object triplets) to convert verbose news articles into structured facts.
3. **Crucible Vetting Layer:** A staging environment using DuckDB to evaluate new facts for conflicts and consensus before permanent storage.
4. **Hybrid Graph/Vector Storage:**
   * **Kùzu (Graph):** Inherently deduplicates knowledge and maps relationships between entities.
   * **Qdrant (Vector):** Enables semantic search for entities (e.g., matching "Apple CEO" to "Tim Cook").
5. **Container-Free Python Orchestration:** A completely dockerless infrastructure initialization process tailored for rapid local iteration and SLM-assistant compatibility.

---

## Architecture Discussion

The system utilizes a multi-tiered pipeline:

* **Tier 1: Ingestion (The Funnel):** Scripts monitor sources (or a Brave Search broker API), strip noise, and normalize output. Raw text is written to an immutable archive (e.g., `/knowledge_base/sources/YYYY/MM`) and assigned a `[Source-ID]`.
* **Tier 2: Fact Extraction (Local SLM Engine):** Target texts are passed to a local SLM (e.g., Llama-3 8B or Qwen-2.5 via Ollama/vLLM). Using libraries like Instructor or Outlines, the SLM is restricted to outputting `KnowledgeTriplet` models, distilling thousands of words into 10–15 structured edges.
* **Tier 3: Algorithmic Vetting (The Staging Crucible):** Extracted triplets are held in a `staging.duckdb` table. A consensus algorithm identifies conflicts against the existing graph, scores based on multi-source verification, and promotes `PENDING` facts to `VERIFIED`.
* **Tier 4: Storage (The Verified Pool):** Verified facts hit the persistent storage layer. Entities become nodes in Kùzu, connected by their extracted predicates. Concurrently, the entities are embedded into Qdrant for semantic flexibility.
* **Tier 5: Context Retrieval (Future Implementation):** When queried, deterministic graph traversals fetch 1st and 2nd-degree connections and return perfectly formatted, cited JSON to the user-facing agent.

---

## Implementation Specifications for Offline SLM Assistants

If you are an offline AI coding assistant extending this codebase, adhere to these guidelines:

* **Python-Native:** Do not introduce Docker, Podman, or external service dependencies unless strictly necessary. Utilize embedded databases: `kuzu` (Graph), `duckdb` (SQL), and `qdrant_client` in local memory/file mode.
* **Dependencies:**

  ```bash
  pip install kuzu qdrant-client duckdb pydantic pandas
  ```

* **Directory Structure (Runtime Generated):**
  * `/data/`: Houses the embedded DB files (`kuzu_db/`, `qdrant_db/`, `staging.duckdb`).
  * `/knowledge_base/sources/`: Immutable artifact archive for raw text ingestion.
* **Database Models:**
  * **DuckDB (Staging):** `staging_triplets` (id, subject, predicate, object, confidence, date, source_id, status)
  * **Kùzu (Graph):** `Node: Entity (id, name, type)` | `Edge: RelatesTo (predicate, confidence, date, source_id)`
  * **Qdrant (Vector):** Collection `entities` storing 384-dimensional dense vectors with payload `{"entity_id": ..., "name": ...}`.
* **Hashing:** Python's built-in `hash()` is non-deterministic per session. Always use `hashlib.sha256().hexdigest()` for generating IDs for Qdrant and Kùzu.

---

## Operation Manual

### 1. Initialization

First, initialize the database schemas. This creates the local files in the `./data/` directory.

```bash
python infrastructure.py
```

### 2. Manual Ingestion Testing

To simulate the broker pulling in a new raw document and generating an immutable source file:

```bash
python ingestion.py
```

### 3. Run the Pipeline

To read the raw archive, extract mock JSON triplets, stage them in DuckDB, and push verified facts to the Graph and Vector databases:

```bash
python pipeline.py
```

### 4. Integration with Local SLMs (Next Steps)

To move from the `SLMExtractor` mock stub to real inference:

1. Ensure Ollama or an OpenAI-compatible vLLM server is running locally (e.g., `http://localhost:11434/api/generate`).
2. Update `extraction.py` to use a structured generation library (`instructor` for OpenAI compat or `outlines`) to ensure the response strictly binds to the `ExtractedFacts` Pydantic class.
