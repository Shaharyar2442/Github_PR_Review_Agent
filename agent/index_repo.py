import os
import chromadb
from chromadb.utils import embedding_functions


# Directories and extensions to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "chroma_db", ".next", ".gemini"}
SKIP_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf", ".lock", ".map"}



def index_repository(repo_path: str):
    """Walk through a repository and index all code files into ChromaDB."""
    print(f" Indexing repository: {repo_path}")

    # Step 1: Create a persistent ChromaDB client
    client = chromadb.PersistentClient(path=os.path.join(repo_path, "chroma_db"))

    # Step 2: Create the embedding function and collection
    from config import GEMINI_API_KEY
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from chromadb import Documents, EmbeddingFunction, Embeddings
    
    class CustomGeminiEmbeddingFunction(EmbeddingFunction):
        def __init__(self, api_key: str):
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
        def __call__(self, input: Documents) -> Embeddings:
            return self.embeddings.embed_documents(input)
            
    embedding_fn = CustomGeminiEmbeddingFunction(api_key=GEMINI_API_KEY)
    
    collection = client.get_or_create_collection(
        name="codebase_gemini", embedding_function=embedding_fn
    )

    # Step 3: Walk the repo and index files
    indexed_count = 0
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories (modifying dirs in-place prevents os.walk from descending)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file_name in files:
            # Skip files with ignored extensions
            _, ext = os.path.splitext(file_name)
            if ext.lower() in SKIP_EXTENSIONS:
                continue

            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, repo_path).replace("\\", "/")

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Skip empty files or very large files (>100KB)
                if not content.strip() or len(content) > 100_000:
                    continue

                # Step 4: Upsert the document into ChromaDB
                collection.upsert(
                    documents=[content],
                    ids=[relative_path],
                    metadatas=[{"file_path": relative_path, "extension": ext}]
                )
                indexed_count += 1
                print(f"  Indexed: {relative_path}")

            except Exception as e:
                print(f"   Skipped {relative_path}: {e}")

    print(f"\n Done! Indexed {indexed_count} files into ChromaDB.")


if __name__ == "__main__":
    # Index the current project directory
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_repository(repo_root)
