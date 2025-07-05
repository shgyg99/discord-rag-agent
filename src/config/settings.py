import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
MODEL_CACHE_DIR = CACHE_DIR / "models"
CACHE_FILE = CACHE_DIR / "embeddings_cache.pkl"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL")
SITE_NAME = os.getenv("SITE_NAME")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

EMBEDDING_MODEL = 'paraphrase-MiniLM-L3-v2'
LLM_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"

DOCS_DIR = "docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

MAX_TOKENS = 150
MAX_CONTEXT_LENGTH = 7000 
DEFAULT_TOP_K = 2
MAX_RETRIES = 3
RETRY_DELAY = 2

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

