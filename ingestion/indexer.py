"""
Indexes parsed game files into ChromaDB for semantic search.
Each game project gets its own isolated ChromaDB collection.
"""

import os
import chromadb
from config import CHROMA_DB_PATH
from ingestion.parser import parse_file
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# One ChromaDB client shared across all indexing operations
_client = chromadb.PersistentClient(path = CHROMA_DB_PATH)

def get_collection(game_name: str):
    
    # Use GPU for embedding if available
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[Indexer] Using device: {device}")

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name = "all-MiniLM-L6-v2",
        device = device
    )

    collection_name = game_name.lower().replace(" ", "_").replace(".", "").replace("-", "_")

    return _client.get_or_create_collection(
        name = collection_name,
        metadata = {"game": game_name},
        embedding_function = embedding_function
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

    SKIP_FOLDERS = {"Library", "Temp", "Logs", "obj", "Build", "Builds", ".git", ".vs"}

    # Collect everything first, then add in one batch
    all_ids = []
    all_documents = []
    all_metadatas = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_FOLDERS]

        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)

            file_chunks = parse_file(filepath)
            if file_chunks is None:
                continue

            for chunk in file_chunks:
                chunk_id = f"{os.path.relpath(filepath, root_path)}::chunk_{chunk['metadata']['chunk_index']}"
                all_ids.append(chunk_id)
                all_documents.append(chunk["content"])
                all_metadatas.append(chunk["metadata"])

    # Add in batches of 100 
    BATCH_SIZE = 100
    for i in range(0, len(all_ids), BATCH_SIZE):
        collection.add(
            ids = all_ids[i:i + BATCH_SIZE],
            documents = all_documents[i:i + BATCH_SIZE],
            metadatas = all_metadatas[i:i + BATCH_SIZE]
        )
        print(f"[Indexer] Embedded {min(i + BATCH_SIZE, len(all_ids))}/{len(all_ids)} chunks...")

    print(f"[Indexer] Indexed '{game_name}' — {len(all_ids)} chunks stored")
    return len(all_ids)


def query_collection(game_name: str, question: str, domain: str = None, n_results: int = 10) -> str:
    """
    Semantic search to find the most relevant chunks for a question.
    Returns a combined string of the top results ready to pass to an agent.
    """

    collection = get_collection(game_name)

    if collection.count() == 0:
        raise RuntimeError(f"[Indexer] No chunks found for '{game_name}'. Run index_project() first.")

    where_filter = None
    if domain == "character":

        # Character files are .cs 
        where_filter = {
            "$and": [
                {"domain": {"$eq": "codebase"}},
                {"extension": {"$eq": ".cs"}}
            ]
        }
    elif domain:
        where_filter = {"domain": {"$eq": domain}}

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