"""
Indexes parsed game files into ChromaDB for semantic search.
Each game project gets its own isolated ChromaDB collection.
"""

import os
import chromadb
from config import CHROMA_DB_PATH
from ingestion.parser import parse_file

# One ChromaDB client shared across all indexing operations
_client = chromadb.PersistentClient(path = CHROMA_DB_PATH)

def get_collection(game_name: str):
    """
    Get or create a ChromaDB collection for a specific game.
    """

    # ChromaDB collection names parser to all lower case
    collection_name = game_name.lower().replace(" ", "_").replace(".", "").replace("-", "_")

    return _client.get_or_create_collection(
        name=collection_name,
        metadata={"game": game_name}
    )


def index_project(game_name: str, root_path: str) -> int:
    """
    Walk the game project folder, parse every file, and store chunks in ChromaDB.
    Returns the total number of chunks indexed.
    """

    collection = get_collection(game_name)

    # Check if this project is already indexed
    existing = collection.count()
    if existing > 0:
        print(f"[Indexer] '{game_name}' already has {existing} chunks")
        return existing

    chunks_indexed = 0

    for dirpath, _, filenames in os.walk(root_path):
        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)

            file_chunks = parse_file(filepath)
            if file_chunks is None:
                continue

            for chunk in file_chunks:

                # append chunk_index to ID 
                chunk_id = f"{os.path.relpath(filepath, root_path)}::chunk_{chunk['metadata']['chunk_index']}"
                collection.add(
                    ids=[chunk_id],
                    documents=[chunk["content"]],
                    metadatas=[chunk["metadata"]]
                )
                chunks_indexed += 1

    print(f"[Indexer] Indexed '{game_name}' and {chunks_indexed} chunks stored")
    return chunks_indexed


def query_collection(game_name: str, question: str, domain: str = None, n_results: int = 5) -> str:
    """
    Semantic search to find the most relevant chunks for a question.
    Returns a combined string of the top results ready to pass to an agent.
    """

    collection = get_collection(game_name)

    if collection.count() == 0:
        raise RuntimeError(f"[Indexer] No chunks found for '{game_name}'. Run index_project() first.")

    # Character questions filter to codebase since character files are .cs
    where_filter = None
    if domain:
        context_domain = "codebase" if domain == "character" else domain
        where_filter = {"domain": context_domain}

    results = collection.query(
        query_texts = [question],
        n_results = n_results,
        where = where_filter
    )

    # Combine top results into one context string for the agent
    documents = results["documents"][0]  # list of matching chunks
    metadatas = results["metadatas"][0]  # list of matching metadata

    context = ""
    for doc, meta in zip(documents, metadatas):
        filename = meta.get("filename", "unknown")
        context += f"\n\n// === {filename} ===\n{doc}"

    return context

