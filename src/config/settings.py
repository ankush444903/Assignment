import os
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Embedding and index configuration
EMBEDDING_FOLDER = os.getenv("EMBEDDING_FOLDER", str(REPO_ROOT / "data" / "embedding"))
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "my_semantic_faiss_index")

# Prompt template file location
PROMPT_TEMPLATE_PATH = os.getenv("PROMPT_TEMPLATE_PATH", str(Path(__file__).resolve().parent / "prompt.txt"))

# Logging defaults
LOG_BASE_DIR = os.getenv("LOG_BASE_DIR", str(REPO_ROOT / "src" / "logs"))
