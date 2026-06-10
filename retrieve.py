from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR = "data/chroma_db"
COLLECTION_NAME = "unofficial_guide"

_model = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query, k=8):
    model = _get_model()
    collection = _get_collection()
    vec = model.encode(query, convert_to_numpy=True).tolist()
    result = collection.query(query_embeddings=[vec], n_results=k)
    hits = []
    for i in range(len(result["documents"][0])):
        hits.append({
            "text": result["documents"][0][i],
            "source": result["metadatas"][0][i]["source"],
            "distance": result["distances"][0][i],
        })
    return hits


TEST_QUERIES = [
    "Which EE professor is easiest to pass?",
    "Does Golovin curve grades?",
    "Who gives the most partial credit?",
    "What do students say about Barba's exams?",
    "Is Pekcan a good professor for circuits?",
]

if __name__ == "__main__":
    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 60)
        results = retrieve(query, k=3)
        for i, r in enumerate(results, start=1):
            snippet = r["text"][:150]
            print(f"  {i}. [source: {r['source']}] (dist: {r['distance']:.4f})")
            print(f"     {snippet}")
