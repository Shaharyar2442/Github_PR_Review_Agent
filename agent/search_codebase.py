import os
import chromadb
from chromadb.utils import embedding_functions

def search_codebase(query: str, n_results: int = 5) -> str:
    """Search the indexed codebase for files related to a natural language query."""

    # Connect to the same persistent ChromaDB
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    client = chromadb.PersistentClient(path=os.path.join(repo_root, "chroma_db"))

    from config import GEMINI_API_KEY
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from chromadb import Documents, EmbeddingFunction, Embeddings
    
    class CustomGeminiEmbeddingFunction(EmbeddingFunction):
        def __init__(self, api_key: str):
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=api_key
            )
        def __call__(self, input: Documents) -> Embeddings:
            return self.embeddings.embed_documents(input)
            
    embedding_fn = CustomGeminiEmbeddingFunction(api_key=GEMINI_API_KEY)
    
    collection = client.get_or_create_collection(
        name="codebase_gemini", embedding_function=embedding_fn
    )

    # Query ChromaDB for the most semantically similar documents
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    # Format the results into a string the LLM can read
    if not results["documents"] or not results["documents"][0]:
        return "No relevant files found in the codebase."

    output = ""
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        file_path = meta.get("file_path", "unknown")
        # Truncate long files to first 80 lines for the LLM context window
        lines = doc.split("\n")
        snippet = "\n".join(lines[:80])
        if len(lines) > 80:
            snippet += f"\n... ({len(lines) - 80} more lines)"

        output += f"\n--- File: {file_path} ---\n{snippet}\n"

    return output


if __name__ == "__main__":
    # Quick test: search for something in your codebase
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "fetch pull request"
    print(f"🔍 Searching for: '{query}'\n")
    print(search_codebase(query))
