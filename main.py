import logging
import os
from dotenv import load_dotenv
from src.rag.retrieval import get_rag_response
from src.config.logging_config import setup_logging
from src.config import settings

load_dotenv()

# Initialize file-based logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logfile = setup_logging(level=LOG_LEVEL, base_log_dir=settings.LOG_BASE_DIR)
logger = logging.getLogger(__name__)
logger.info("Starting application; logfile=%s", logfile)


def main():
    #logger.info("Starting Loan Product Assistant (RAG) interactive CLI")

    while True:
        try:
            query = input("\n Enter your question (or 'quit' to exit): ")
        except (EOFError, KeyboardInterrupt):
            logger.info("Received exit signal. Shutting down.")
            break

        if query.lower() in ["quit", "exit", "q"]:
            logger.info("User requested exit.")
            print("👋 Goodbye!")
            break

        if not query.strip():
            continue

        logger.info("Running RAG query")
        logger.debug("Query: %s", query)
        # reduce console noise: RAG start is debug-level

        # Call the RAG function from the other file
        response = get_rag_response(query)

        print("\n### RAG Response ###")
        print(response)


if __name__ == "__main__":
    main()