import os
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()
try:
    from src.config.logging_config import setup_logging
    from src.config import settings
    logfile = setup_logging(base_log_dir=settings.LOG_BASE_DIR)
    logger = logging.getLogger(__name__)
    logger.info("Chunking/indexing run; logfile=%s", logfile)
except Exception:

    from pathlib import Path
    from datetime import datetime
    def _setup_local():
        repo_root = Path(__file__).resolve().parents[2]
        log_root = repo_root / "src" / "logs"
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        folder = log_root / date_str
        folder.mkdir(parents=True, exist_ok=True)
        logfile = folder / f"run_{datetime.utcnow().strftime('%H%M%S')}.log"
        logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
        fh = logging.FileHandler(logfile, encoding="utf-8")
        logging.getLogger().addHandler(fh)
        return str(logfile)

    logfile = _setup_local()
    logger = logging.getLogger(__name__)
    logger.info("Chunking/indexing run (fallback); logfile=%s", logfile)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_FOLDER = os.getenv("CLEANED_FOLDER", os.path.join(REPO_ROOT, "data", "cleaned"))
OUTPUT_FOLDER = os.getenv("EMBEDDING_FOLDER", os.path.join(REPO_ROOT, "data", "embedding"))
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "my_semantic_faiss_index")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

if not os.getenv("OPENAI_API_KEY"):
    logger.error("FATAL ERROR: OPENAI_API_KEY is not set. Please check your .env file.")
    raise SystemExit(1)

if not os.path.exists(INPUT_FOLDER):
    logger.error("FATAL ERROR: Input folder '%s' does not exist.", INPUT_FOLDER)
    raise SystemExit(1)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logger.info("Initializing embeddings (model=%s)", EMBEDDING_MODEL)
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

vectorstore_path = os.path.join(OUTPUT_FOLDER, FAISS_INDEX_NAME)
try:
    logger.info("Checking for existing vectorstore at %s...", vectorstore_path)
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    logger.info("Loaded existing vectorstore - skipping creation")

except Exception:
    logger.info("Vectorstore not found. Creating new one...")


    logger.info("Loading all .txt files from: %s", INPUT_FOLDER)
    loader = DirectoryLoader(path=INPUT_FOLDER, glob="**/*.txt", loader_kwargs={"autodetect_encoding": True})
    raw_documents = loader.load()
    logger.info("Successfully loaded %d raw document(s).", len(raw_documents))


    logger.info("Applying Semantic Chunking...")
    all_text = "\n\n".join([doc.page_content for doc in raw_documents])

    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=95,
    )

    semantic_chunks = text_splitter.create_documents([all_text])
    logger.info("Original text split into %d semantic chunks.", len(semantic_chunks))

    logger.info("Creating FAISS index...")
    vectorstore = FAISS.from_documents(documents=semantic_chunks, embedding=embeddings)
    vectorstore.save_local(folder_path=OUTPUT_FOLDER, index_name=FAISS_INDEX_NAME)
    logger.info("Created and saved new vectorstore to %s", OUTPUT_FOLDER)

logger.info("Pipeline complete! Vectorstore ready at: %s", vectorstore_path)
