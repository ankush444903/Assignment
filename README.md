# Loan Product Assistant — Bank of Maharashtra (RAG PoC)

## Overview
This repository is a proof-of-concept Retrieval-Augmented Generation (RAG) assistant that answers questions about Bank of Maharashtra loan products. It scrapes loan pages, stores cleaned text in data/cleaned/, builds a FAISS semantic index under data/embedding/, and answers queries by retrieving relevant chunks and invoking an LLM.

## Quick Start

1. Create and activate a virtual environment (Windows PowerShell):

powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt


2. (Optional) Install LangChain helpers if you plan to use LangChain patterns:

powershell
pip install langchain langchain-community


3. Copy environment template and set API key(s):

powershell
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY (or other provider credentials)


4. (Optional) Scrape website pages to populate data/cleaned/:

powershell
python -m src.webscraping.webscraping


5. Create embeddings and FAISS index:

powershell
python "src/processing/Chunking & FAISS Indexing.py"


6. Run the interactive CLI assistant:

powershell
python main.py


Type a question at the prompt; enter quit or exit to stop.

## Files of Interest

- main.py — CLI entrypoint for interactive queries.
- src/webscraping/webscraping.py — scrapes and writes cleaned page text to data/cleaned/.
- src/processing/Chunking & FAISS Indexing.py — loads cleaned text and builds FAISS index/embeddings.
- src/rag/retrieval.py — loads FAISS, sets up retriever and LLM, exposes get_rag_response().

## Libraries

- requests, beautifulsoup4 — web scraping.
- python-dotenv — load .env variables.
- faiss-cpu — local vector similarity search.
- sentence-transformers / OpenAIEmbeddings — embeddings provider.
- openai and optional langchain packages — LLM and orchestration helpers.

Install required packages with pip install -r requirements.txt. If you encounter import errors for LangChain helpers, install langchain and langchain-community or adapt the code to a single provider SDK.

## Notes & Troubleshooting

- Some pages may be JS-driven; the current scrapers use requests + BeautifulSoup and only work on server-rendered HTML.
- If the FAISS index is missing, run the chunking/indexing script to generate data/embedding/*.faiss and related files.
- Logging: set LOG_LEVEL in .env to control console/file verbosity.

## Next Steps

- I can run an import check and a local smoke test to verify main.py runs and logging behaves as expected. Tell me if you want me to run those now.

