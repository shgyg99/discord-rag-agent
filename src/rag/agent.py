from sentence_transformers import SentenceTransformer
import os
from typing import List, Tuple, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import numpy as np
import faiss
import pickle
import time
from ..config.settings import *
from openai import OpenAI


class DocumentLoader:
    def __init__(self, docs_dir: str = DOCS_DIR, cache_file: str = CACHE_FILE):
        self.docs_dir = docs_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.embeddings = []
        
        # Create cache directory
        os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
        
        # Initialize sentence transformer
        print("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            cache_folder=MODEL_CACHE_DIR
        )
        
        self.cache_file = cache_file
        self.embedding_cache = self._load_cache()
        print("Sentence transformer model loaded!")

    def _load_cache(self) -> Dict[str, List[float]]:
        """Load cached embeddings if they exist."""
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    def _save_cache(self):
        """Save embeddings cache to disk."""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.embedding_cache, f)

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers."""
        try:
            # Convert to numpy array and then to list
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [hash(text) % 1024 for _ in range(384)]  # MiniLM uses 384 dimensions

    def load_and_chunk_documents(self) -> Tuple[List[str], List[List[float]]]:
        start_time = time.time()
        chunks = []
        embeddings = []
        docs_path = Path(self.docs_dir)

        print(f"\n{'=' * 50}\nStarting document loading process...")

        # First, collect all chunks
        files_found = list(docs_path.glob("*.txt"))
        print(f"Found {len(files_found)} text files in {self.docs_dir}")

        for file_path in files_found:
            print(f"\nProcessing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                new_chunks = self.text_splitter.split_text(content)
                print(f"Generated {len(new_chunks)} chunks from file")
                chunks.extend(new_chunks)

        print(f"\nTotal chunks generated: {len(chunks)}")
        print("Starting embedding generation...")

        # Process chunks in batches
        total_batches = len(chunks) // 5 + (1 if len(chunks) % 5 else 0)
        for i in range(0, len(chunks), 5):
            batch = chunks[i:i + 5]
            print(f"\nProcessing batch {i // 5 + 1}/{total_batches}")
            batch_embeddings = []

            for chunk in batch:
                if chunk in self.embedding_cache:
                    print("✓ Using cached embedding")
                    batch_embeddings.append(self.embedding_cache[chunk])
                else:
                    print("⚡ Generating new embedding")
                    embedding = self.generate_embedding(chunk)
                    self.embedding_cache[chunk] = embedding
                    batch_embeddings.append(embedding)

            embeddings.extend(batch_embeddings)

        print(f"\nEmbedding generation complete. Total embeddings: {len(embeddings)}")
        print(f"{'=' * 50}\n")
        return chunks, embeddings


class VectorStore:
    def __init__(self, dimension: int = 384):  # MiniLM dimension
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity
        self.texts = []  # Store original texts

    def add_embeddings(self, texts: List[str], embeddings: List[List[float]]):
        """Add embeddings to the FAISS index"""
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.texts.extend(texts)

    def search(self, query_embedding: List[float], k: int = 3) -> List[str]:
        """Search for most similar documents"""
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, k)
        return [self.texts[i] for i in indices[0]]


class Retriever:
    def __init__(self, document_loader: DocumentLoader, vector_store: VectorStore):
        self.document_loader = document_loader
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """
        Convert query to embedding and retrieve most relevant documents.
        """
        try:
            # Generate embedding for the query
            query_embedding = self.document_loader.generate_embedding(query)

            # Get most similar documents
            relevant_docs = self.vector_store.search(query_embedding, k=k)

            return relevant_docs
        except Exception as e:
            print(f"Error in retrieval: {e}")
            return []


class Generator:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )
        self.model = LLM_MODEL
        self.response_cache = {}
        self.max_retries = MAX_RETRIES

    def construct_prompt(self, query: str, context: List[str]) -> str:
        """Construct a detailed prompt for the LLM."""
        context_str = "\n".join(context)
        return f"""Based on the following context, answer the question.
If you don't know the answer, just say that you don't know.

Context:
{context_str}

Question: {query}"""

    def generate(self, query: str, context: List[str]) -> str:
        """Generate a response using OpenRouter API via OpenAI client."""
        cache_key = (query, tuple(context))
        if cache_key in self.response_cache:
            print("Using cached response")
            return self.response_cache[cache_key]

        prompt = self.construct_prompt(query, context)

        for attempt in range(self.max_retries):
            try:
                print(f"Generation attempt {attempt + 1}/{self.max_retries}")
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on given context."},
                        {"role": "user", "content": prompt}
                    ],
                    extra_headers={
                        "HTTP-Referer": SITE_URL,
                        "X-Title": SITE_NAME
                    }
                )
                
                response = completion.choices[0].message.content
                if response:
                    print("Successfully generated response")
                    self.response_cache[cache_key] = response
                    return response
                
            except Exception as e:
                print(f"Error in generation attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return "I apologize, but I encountered an error while generating the response. Please try again."
                time.sleep(RETRY_DELAY)

        return "I apologize, but I was unable to generate a response after multiple attempts."


class RAGAgent:
    def __init__(self):
        print("\nInitializing RAG Agent...")
        start_time = time.time()

        print("1. Loading document loader...")
        self.document_loader = DocumentLoader()

        print("2. Processing documents and generating embeddings...")
        self.chunks, self.embeddings = self.document_loader.load_and_chunk_documents()

        print("3. Initializing vector store...")
        self.vector_store = VectorStore()
        print(f"Adding {len(self.embeddings)} embeddings to vector store...")
        self.vector_store.add_embeddings(self.chunks, self.embeddings)

        print("4. Setting up retriever and generator...")
        self.retriever = Retriever(self.document_loader, self.vector_store)
        self.generator = Generator()

        self.max_context_length = MAX_CONTEXT_LENGTH

        print(f"Initialization complete! Time taken: {time.time() - start_time:.2f} seconds\n")

    def query(self, input_text: str) -> str:
        """Execute the full RAG chain with detailed logging."""
        try:
            print(f"\n{'=' * 50}")
            print(f"Processing query: '{input_text}'")
            start_time = time.time()

            print("\n1. Retrieving relevant documents...")
            retrieval_start = time.time()
            relevant_docs = self.retriever.retrieve(input_text, k=DEFAULT_TOP_K)

            # Truncate context if too long
            total_context = " ".join(relevant_docs)
            if len(total_context) > self.max_context_length:
                relevant_docs = relevant_docs[:2]  # Further limit context

            print(f"Found {len(relevant_docs)} relevant documents")
            print(f"Retrieval time: {time.time() - retrieval_start:.2f} seconds")

            if not relevant_docs:
                print("No relevant documents found!")
                return "I'm sorry, I couldn't find relevant information to answer your question."

            print("\n2. Generating response...")
            generation_start = time.time()
            response = self.generator.generate(input_text, relevant_docs)
            if not response:
                return "I apologize, but I couldn't generate a response. Please try again."
            print(f"Generation time: {time.time() - generation_start:.2f} seconds")

            print(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")
            print(f"{'=' * 50}\n")
            return response
        except Exception as e:
            print(f"Error in RAG chain: {str(e)}")
            return "An error occurred while processing your request. Please try again."


