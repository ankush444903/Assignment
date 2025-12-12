
####  semantic base search and retrieval data  #####
import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from typing import Optional, Dict
from pathlib import Path
from src.config import settings
from src.config.logging_config import setup_logging

logfile = setup_logging(base_log_dir=settings.LOG_BASE_DIR)
logger = logging.getLogger(__name__)
logger.info("Logging initialized; logfile=%s", logfile)
load_dotenv()
vectorstore_path = settings.EMBEDDING_FOLDER
FAISS_INDEX_NAME = settings.FAISS_INDEX_NAME
llm = None
embeddings = None
try:
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=llm_model, temperature=float(os.getenv("LLM_TEMPERATURE", "0")))
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    logger.info("LLM and Embeddings initialized (llm=%s, embed_model=%s)", llm_model, os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
except Exception as e:
    logger.exception("Failed to initialize models: %s", e)


def _load_vectorstore(folder_path: str, index_name: str):
    required_files = [f"{index_name}.faiss", f"{index_name}.pkl"]
    if not all(os.path.exists(os.path.join(folder_path, f)) for f in required_files):
        logger.error("Missing FAISS files in %s. Required: %s", folder_path, required_files)
        return None

    logger.info("Loading FAISS vectorstore from %s (index=%s)", folder_path, index_name)
    vectorstore = FAISS.load_local(
        folder_path=folder_path,
        embeddings=embeddings,
        index_name=index_name,
        allow_dangerous_deserialization=True,
    )
    logger.info("Vectorstore loaded successfully")
    return vectorstore

vectorstore = None
try:
    vectorstore = _load_vectorstore(vectorstore_path, FAISS_INDEX_NAME)
    if vectorstore is None:
        logger.warning("Vectorstore not available; RAG queries will not run until index is created.")
except Exception:
    logger.exception("Unable to initialize vectorstore.")

retriever = None
RAG_CHAIN = None
if vectorstore is not None and llm is not None:
    retriever = vectorstore.as_retriever(search_kwargs={"k": int(os.getenv("RETRIEVER_K", "8"))})
    prompt_path = Path(settings.PROMPT_TEMPLATE_PATH)
    if prompt_path.exists():
        try:
            template = prompt_path.read_text(encoding="utf-8")
            logger.info("Loaded prompt template from %s", prompt_path)
        except Exception as e:
            logger.exception("Failed to read prompt template: %s", e)
            template = "You are a helpful assistant that answers questions based **only** on the following context.\n---\nContext: {context}\n---\nQuestion: {input}\nAnswer:\n"
    else:
        logger.warning("Prompt template not found at %s; using fallback template.", prompt_path)
        template = "You are a helpful assistant that answers questions based **only** on the following context.\n---\nContext: {context}\n---\nQuestion: {input}\nAnswer:\n"

    prompt = ChatPromptTemplate.from_template(template)

    # Setup RAG pipeline (The main chain, initialized once)
    RAG_CHAIN = ({"context": retriever, "input": RunnablePassthrough()} | prompt | llm | StrOutputParser())


def get_rag_response(query: str) -> str:
    """Invoke the RAG chain with a user query. Returns the LLM answer or an error message."""
    logger.debug("Invoking RAG for query: %s", query)
    if RAG_CHAIN is None:
        logger.error("RAG chain is not initialized. Ensure embeddings/FAISS index and LLM are available.")
        return "RAG is not ready: missing vectorstore or LLM. Please run the embedding pipeline and set model credentials."

    try:
        response = RAG_CHAIN.invoke(query)
        logger.debug("RAG response length=%d", len(response) if isinstance(response, str) else 0)
        return response
    except Exception as e:
        logger.exception("RAG execution failed: %s", e)
        return f"RAG Execution Error: {e}"

