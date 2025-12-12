# Loan Product Assistant — Bank of Maharashtra (RAG PoC)

## Project Overview & Goal
This repository contains a proof-of-concept Retrieval-Augmented Generation (RAG) pipeline to answer questions about Bank of Maharashtra loan products. The system scrapes loan pages, consolidates cleaned text, builds a FAISS semantic index, and answers user questions by retrieving relevant chunks and invoking an LLM.

## Quick Start
1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Additional recommended packages
pip install langchain langchain-openai langchain-community
```

2. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (or other provider credentials):

```powershell
copy .env.example .env
# then edit .env in an editor and add your OPENAI_API_KEY
```

3. (Optional) Scrape official pages to populate `data/cleaned`:

```powershell
python -m src.webscraping.webscraping
```

4. Create embeddings / FAISS index:

```powershell
python src/processing/"Chunking & FAISS Indexing.py"
```

5. Run the interactive assistant:

```powershell
python main.py
```


## Architectural Decisions
- Project layout: small src package with modules for `webscraping`, `processing`, and `rag` to keep responsibilities separated.
- Data files: cleaned text files stored under `data/cleaned/` and FAISS index files under `data/embedding/`.
- Lightweight vector store: FAISS local index stored on disk to keep dependency minimal and easy to reproduce.

## Libraries and Why
- `requests`, `beautifulsoup4`: robust, minimal web scraping stack.
- `python-dotenv`: simple environment config loading.
- `faiss-cpu`: fast vector similarity search locally.
- `openai` (or other provider) + `langchain*` helpers: to generate embeddings and call the LLM.
- `logging` (stdlib): structured logs for observability and debugging.

Note: The repository uses some `langchain_*` packages in code. If you prefer, replace with stable `langchain` primitives or the provider SDK you use.

## Data Strategy & Chunking
- The pipeline first scrapes pages, cleans noise (headers, footers, scripts), extracts tables and text segments, and saves a single cleaned `.txt` per page.
- For embedding creation the code uses semantic chunking (via `SemanticChunker` in the original implementation). This approach preserves semantic boundaries better than naive fixed-size splits.
- Retriever config: `k=5` by default, configurable via `.env` (`RETRIEVER_K`).

## Model Selection
- Embeddings: default `text-embedding-3-small` (OpenAI) — compact and cost-effective.
- LLM: default `gpt-4o-mini` as used in code; changeable via `LLM_MODEL` in `.env`.
- Rationale: balance quality and cost for a proof-of-concept; these choices are configurable.

## How the RAG flow works
1. Convert user query to text and pass to retriever.
2. Retriever finds top-k relevant chunks using FAISS.
3. The chunks are inserted into a prompt template and sent to the LLM.
4. The LLM responds; the system returns the answer to the user.

## Files of Interest
- `main.py` — CLI entrypoint for interactive queries.
- `src/webscraping/webscraping.py` — scrapes and writes cleaned page text to `data/cleaned`.
- `src/processing/Chunking & FAISS Indexing.py` — loads cleaned text and builds FAISS index.
- `src/rag/retrieval.py` — loads FAISS, sets up retriever and LLM, exposes `get_rag_response()`.

## Challenges and Notes
- Some Bank of Maharashtra pages may have dynamic content or JS-driven elements; the current scrapers use `requests` and `BeautifulSoup` so they only work for server-rendered HTML.
- The code references `langchain_*` helper packages. If you encounter import errors, prefer installing `langchain`, `openai`, and `langchain-community` or adjust the code to use the provider SDK directly.

## Potential Improvements
- Add unit tests for parsing and retrieval components.
- Add retry/backoff and rate-limiting for scraping and API calls.
- Replace FAISS with a managed vector DB for production scale.
- Add provenance and source attribution to LLM responses.
- Add a lightweight web UI or Flask endpoint to serve queries.

## Next Steps I can help with
- Run the embedding build and validate FAISS index loading on your machine.
- Convert `Chunking & FAISS Indexing.py` into a proper CLI module and add automated tests.

---
If you'd like, I can now run quick checks (imports, path validation) and patch anything else to make the repo runnable on your machine. Tell me which step you'd like next.
