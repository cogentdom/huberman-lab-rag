# Huberman Lab RAG — Presentation notes (comprehensive)

Use this document as **introductory input** when drafting slides, speaker notes, or a talk outline. It is written to be **factually aligned** with the current codebase and docs; adjust tone and depth for your audience (technical vs general).

---

## 1. Elevator pitch (10–20 seconds)

**Huberman Lab RAG** is a small web application that answers natural-language questions by **retrieving relevant passages** from **Huberman Lab podcast transcripts** and **generating a response** with an LLM, so answers stay **grounded in retrieved context** rather than pure model memory.

**One line:** *Semantic search over podcast chunks + OpenAI chat completion with injected context.*

---

## 2. Audience and learning goals

**Possible audiences**

- Engineers learning **RAG** end-to-end
- Hiring managers / reviewers evaluating a **portfolio project**
- Students comparing **vector DB** options (here: **Redis Stack / RediSearch**)

**What they should take away**

- What problem RAG solves vs “chat only”
- How **embeddings → index → retrieval → prompt assembly → generation** fits together
- How this repo is **runnable** (Docker-first) and **where** each concern lives in the tree
- Honest **limitations** (no live podcast sync, API costs, medical disclaimer territory)

---

## 3. Problem statement (why RAG?)

**Without RAG**

- General-purpose models may **hallucinate** or give **generic** health/performance advice
- They **cannot cite** specific episode content unless that content was in training data—and even then, provenance is weak

**With RAG (this project)**

- The model’s answer is **conditioned on chunks** retrieved for *this* query from *this* corpus (transcript-derived)
- You control the **corpus** and can update embeddings/index when content changes
- Trade-off: quality depends on **chunking**, **embedding model**, **top-K**, and **prompt design**

**Framing for a slide:** *Ground answers in a known document set (podcast transcripts), not in vague parametric memory.*

---

## 4. Scope: what this project is and is not

**Is**

- A **demonstration** of transcript-grounded Q&A
- A **Flask** app with a simple **web UI** and **`POST /query` JSON API**
- A **Redis Stack** deployment with **vector search** (KNN) over indexed documents
- **Docker Compose** orchestration with **persistent Redis** and **bootstrap/restore** affordances

**Is not**

- An official Huberman Lab product
- A replacement for medical advice (see **§15 Ethics / disclaimers**)
- A full **MLOps** pipeline with automated re-ingestion from YouTube/podcast feeds (data is **bundled/assumed** under `app/data/` and related assets)
- Guaranteed to surface **verbatim citations** with timestamps in the user-visible answer (roadmap item in README)

---

## 5. User-visible experience

1. User opens the app (browser) or calls the API.
2. User asks a question (e.g. sleep, light, dopamine, protocols).
3. Backend **embeds the query**, runs **vector search** in Redis, pulls **top-K** chunks.
4. Backend builds a **system prompt** = base instructions from `app/prompt.txt` + **numbered context documents** (title + chunk text).
5. Backend calls **OpenAI chat completions** and returns the assistant text to the UI/API.

**Screenshot / visual asset (for slides)**

- README references an interface preview image:  
  `https://cogentdom.wordpress.com/wp-content/uploads/2026/02/huberman-lab-rag-interface.png`

---

## 6. Core concepts (teaching block, 2–4 minutes)

### 6.1 Embeddings

- Text is mapped to a **dense vector** so that *semantically similar* texts are *closer* in vector space (for a given model).
- This project uses OpenAI **`text-embedding-3-small`** for both **offline** (data prep) and **online** (query embedding)—**keep models consistent** between index and query.

### 6.2 Vector index

- Vectors and metadata are stored in Redis documents; a **RediSearch** index (name: **`embeddings-index`**) enables **KNN** queries over the **`content_vector`** field (cosine-style distance as configured in setup).

### 6.3 Retrieval

- **Top-K** (code uses **K = 10** in `process_query`) nearest chunks to the query embedding are returned as candidate context.

### 6.4 Generation

- Retrieved chunks are concatenated into the **system** message content (via assembled prompt file), and the **user** message is the raw question.
- Model: **`gpt-4o-mini`** in `app/utils.py` (temperature **0.7**, max tokens **1000**)—note these knobs affect creativity vs faithfulness.

---

## 7. Data assets (offline world)

**Expected under `app/data/` (conceptually)**

- **`embeddings.csv`** — tabular data joining **video keys**, **chunk keys**, and **vector fields** (e.g. `content_vector`, `title_vector`) used to populate Redis
- **`title_dict.pkl`** — maps **video key → episode title**
- **`chunk_dict.pkl`** — maps **chunk key → transcript text** for that chunk

**Why pickles + CSV**

- Pickles provide fast lookup structures for **titles** and **chunk bodies** at answer time; CSV carries the **embedding rows** for bulk indexing.

**Chunk key convention (used in code)**

- Keys encode video + chunk index, e.g. split on **`_chunk_`** to recover **video key** and **chunk index** (`get_video_key`, `get_chunk_index` in `app/utils.py`).

**Important presentation point**

- The repo documents **how to run** the system; **large generated assets** may be gitignored or supplied separately—speak to **your** distribution choice if you demo from a fork.

---

## 8. Online request path (code-level narrative)

**Entry**

- `app/app.py` — Flask routes:
  - **`GET /`** → `templates/index.html`
  - **`POST /query`** → JSON `{"query": "..."}` → `process_query`

**Core pipeline**

- `app/utils.py`
  - **`search_redis`** — embed query with OpenAI, run RediSearch **KNN** query, return document fields including **`title`**, **`text`**, **`chunk_key`**, **`vector_score`**
  - **`add_context`** — reads `prompt.txt`, appends each retrieved chunk as `### Context Document i` with title + content; writes debug/history under `app/chat_history/prompts/`
  - **`process_query`** — orchestrates search → context assembly → **`chat.completions.create`** → writes response under `app/chat_history/` → returns string

**Prompt template**

- `app/prompt.txt` defines **persona** (“helpful assistant for Huberman Lab…”) and **style instructions**; retrieved chunks are **appended** programmatically.

**Optional slide: “two-stage prompt”**

1. Static **identity + instructions** (`prompt.txt`)
2. Dynamic **evidence section** (retrieved chunks)

---

## 9. Index creation (bootstrap)

**Local development**

- `app/setup_vector_db.py` — loads CSV + pickles, merges frames, defines Redis schema (**`TextField`** for title/text, **`VectorField`** for vectors), creates index **`embeddings-index`**, bulk loads documents with **`PREFIX`** (e.g. `doc`).

**Docker**

- `docker-setup_vector_db.py` — Docker-oriented variant (paths/host differ)
- `docker-init-data.sh` — operator script referenced in README for first-time initialization

**Presentation tip**

- Show **one diagram**: *offline ETL/embeddings → CSV/pickles → index script → Redis* vs *online query → embed → KNN → LLM*.

---

## 10. Infrastructure (Docker Compose)

**Services (`docker-compose.yml`)**

- **`redis`** — `redis/redis-stack:latest`, ports **6379** (Redis) and **8001** (RedisInsight UI), **volume** `redis_data` for persistence, optional **seed** from `app/redis_backup_20250619_064236.rdb` when empty
- **`app`** — built from repo **`Dockerfile`**, port **8000**, reads **`.env`**, sets **`REDIS_HOST=redis`**, mounts **`./app/data` read-only** into the container, uses **`app_chat_history`** volume for writable prompt/response logs

**Healthchecks**

- Redis: `redis-cli ping`
- App: HTTP GET to `/` inside container

**Operator scripts (README)**

- `./docker-start.sh` — bring stack up
- `./docker-init-data.sh` — first-run vector initialization

**Supporting automation**

- `docker-entrypoint.sh` — startup orchestration
- `auto-restore.py` — index existence / restore logic (paired with Redis flags/behavior documented in `DOCKER_README.md`)

---

## 11. Configuration and secrets

**Environment (`env.template`)**

- **`OPENAI_API_KEY`** — required for embeddings + chat
- **`FLASK_ENV`** — `production` in template / compose defaults
- **`REDIS_HOST`**, **`REDIS_PORT`**, **`REDIS_PASSWORD`** — set for Docker via compose; local defaults to localhost

**Security talking points**

- Never commit **`.env`** (gitignored)
- Read-only mount for **`app/data`** in Docker reduces accidental corpus tampering from the app container
- API keys in slide decks: **redact**; use env vars in demos

---

## 12. API demo (for live or recorded demo)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What does Huberman say about sleep protocols?"}'
```

**Narration**

- Emphasize **JSON in/out** for integration tests or another frontend
- Compare **UI** vs **API** as same backend

---

## 13. Project tree (speaker map)

Use this to answer “where is X?”

- **`app/app.py`** — Flask app
- **`app/utils.py`** — retrieval + OpenAI + prompt assembly
- **`app/templates/index.html`** — UI
- **`app/prompt.txt`** — static system prompt skeleton
- **`app/setup_vector_db.py`** — local index build
- **`docker-setup_vector_db.py`** — Docker index build
- **`docker-compose.yml`**, **`Dockerfile`**, **`docker-entrypoint.sh`** — container story
- **`auto-restore.py`** — Redis index restore helper
- **`QUICKSTART.md`**, **`DOCKER_README.md`**, **`CONTRIBUTING.md`**, **`README.md`** — human docs

---

## 14. Design decisions worth mentioning

- **Redis Stack** instead of a separate vector DB — fewer moving parts for a portfolio-scale demo; still “real” RediSearch vector queries
- **Precomputed embeddings** in CSV — faster onboarding than re-embedding entire corpus on every setup (at cost of regeneration pipeline when corpus changes)
- **K = 10** — richer context vs noise/latency/cost; a good interview talking point (“how I’d tune/evaluate K”)
- **Separate title/text fields + chunk_key** — enables future hybrid filters (`create_hybrid_field` exists as a hook) even if default search uses `hybrid_fields="*"`

---

## 15. Limitations, risks, and ethics

**Technical**

- Retrieval quality depends on **chunking strategy** and **embedding model**; bad chunks → **lost evidence**
- **No automated evaluation** in-repo (README roadmap: retrieval metrics, tests)
- **Prompt file** includes a placeholder/example mismatch (e.g. sample user question vs unrelated assistant text)—worth acknowledging as **content debt**, not core architecture
- **Temperature > 0** can introduce phrasing drift; lower temperature if you want stricter grounding tone

**Product / trust**

- Health-adjacent content: present as **educational** and **non-diagnostic**
- Encourage users to consult professionals for medical decisions
- If you claim “grounded in podcast,” clarify **grounded in retrieved chunks**, not guaranteed **verbatim quotes** or **timestamps**

**Operational**

- OpenAI **cost** scales with tokens (context size ↑ with K and chunk length)
- Dependency on **third-party API** availability and policy

---

## 16. Roadmap (from README — slide-ready)

- Evaluation metrics for **retrieval quality**
- Automated **tests** for query + index lifecycle
- Optional **source citations** (episode titles already in context assembly; surfacing them in the final answer is a UX/product choice)
- **CI** for format/lint/docs links

**Optional extensions to mention as “next iteration”**

- Hybrid **BM25 + vector** retrieval
- Re-ranking cross-encoder
- User feedback loop on bad answers
- Streaming responses in the UI

---

## 17. Suggested slide outline (fill from sections above)

1. Title — Huberman Lab RAG
2. Problem — trustworthy, corpus-specific Q&A
3. Solution — RAG loop (diagram)
4. Demo screenshot / 30s screen recording
5. Data — transcripts → chunks → embeddings → Redis
6. Query path — embed, KNN, prompt, generate
7. Stack — Flask, OpenAI, Redis Stack, Docker
8. Runbook — Docker vs local (one slide)
9. API example
10. Limitations & ethics
11. Roadmap / future work
12. Q&A

---

## 18. Demo runbook (step-by-step, Docker)

**Pre-demo**

- Docker running, `.env` with valid **`OPENAI_API_KEY`**
- Pull / build images if needed

**Steps**

1. `./docker-start.sh`
2. First time (or fresh volume): `./docker-init-data.sh`
3. Open **`http://localhost:8000`**
4. Ask 2–3 questions with different specificity (broad vs narrow)
5. Optional: show **RedisInsight** at **`http://localhost:8001`**
6. Optional: `curl` **`POST /query`**

**Fallback if network flaky**

- Pre-record a short video; keep **curl** output in slides

---

## 19. Local runbook (short)

- Python **3.12**, `pip install -r requirements.txt`
- Redis on **6379**
- `python app/setup_vector_db.py` after data present
- `./run_app.sh`

(Details: `QUICKSTART.md`.)

---

## 20. Q&A preparation (likely questions + answer sketches)

**Why Redis for vectors?**

- Integrated **RediSearch** module, Docker-friendly, persistent volume; good for demo scale and learning.

**Why precomputed embeddings?**

- Faster setup and stable costs for demos; regeneration is a separate batch job when corpus updates.

**How do you prevent hallucinations?**

- RAG **reduces** but does not eliminate them; mitigations include better retrieval, re-ranking, lower temperature, requiring citations, evaluation harness.

**How would you measure quality?**

- Retrieval: nDCG/MRR on labeled queries; generation: groundedness checks, human eval, LLM-as-judge with caution.

**Can it search a specific episode only?**

- Architecture supports **filtering** via RediSearch query string (`create_hybrid_field` hook); productize as UI filters.

**Costs?**

- Embeddings per query + large system prompt (many chunks) + completion tokens; optimize with smaller K, shorter chunks, summarization of context.

---

## 21. Vocabulary cheat sheet (for mixed audiences)

- **RAG** — Retrieval-Augmented Generation
- **Embedding** — vector representation of text
- **KNN** — k-nearest neighbors search in vector space
- **RediSearch** — Redis module for secondary indexing and vector search
- **Redis Stack** — Redis distribution bundling modules (Search, JSON, etc.)
- **Chunk** — transcript segment used as retrieval unit
- **Top-K** — retrieve K best matches by similarity

---

## 22. Closing lines (optional)

- *“This project is a compact reference implementation: real vector search, real LLM calls, and a clear seam between offline indexing and online retrieval.”*
- *“The interesting engineering moves from ‘call an API’ to ‘shape the corpus, retrieval, and prompt so answers match user expectations.’”*

---

_End of notes. Trim or expand sections per talk length; keep numbers (ports, index name, models) synchronized with code when you change them._
