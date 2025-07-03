import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
MODEL_CACHE_DIR = CACHE_DIR / "models"
EMBEDDINGS_CACHE_DIR = CACHE_DIR / "embeddings"

# Cache files
CACHE_FILE = EMBEDDINGS_CACHE_DIR / "embeddings_cache.pkl"

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")
SITE_NAME = os.getenv("SITE_NAME")

# Model Configuration
EMBEDDING_MODEL = 'paraphrase-MiniLM-L3-v2'
LLM_MODEL = "google/gemma-3-4b-it:free"

# OpenRouter Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
VERIFY_SSL = True  # Set to False if SSL verification issues persist

# Document Processing
DOCS_DIR = "docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Generation Settings
MAX_TOKENS = 150
TIMEOUT = 30
MAX_CONTEXT_LENGTH = 1000
DEFAULT_TOP_K = 2
REQUEST_TIMEOUT = 60  # Increased timeout for SSL handshake
MAX_RETRIES = 3
RETRY_DELAY = 2
