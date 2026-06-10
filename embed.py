import json
from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_FILE = "data/chunks/chunks.json"
CHROMA_DIR = "data/chroma_db"
COLLECTION_NAME = "unofficial_guide"

def main():
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [c["text"] for c in chunks]
    print("Embedding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{"source": c["source"], "chunk_id": c["chunk_id"]} for c in chunks],
    )

    print(f"Embedded and stored {len(chunks)} chunks in collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()
