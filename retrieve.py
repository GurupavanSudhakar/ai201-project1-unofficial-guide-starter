from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR = "data/chroma_db"
COLLECTION_NAME = "unofficial_guide"

PROFESSOR_MAP = {
    "golovin":     "andrii_golovin.txt",
    "barba":       "joseph_barba.txt",
    "kreminska":   "liubov_kreminska.txt",
    "khrais":      "nidal_khrais.txt",
    "ho":          "ping-pei_ho.txt",
    "reyes":       "julio_reyes.txt",
    "uyar":        "m_umit_uyar.txt",
    "duale":       "ali_duale.txt",
    "sun":         "yi_sun.txt",
    "dorsinville": "roger_dorsinville.txt",
    "saeed":       "samah_saeed.txt",
    "cano":        "alfredo_cano_martinez.txt",
    "pekcan":      "hakan_pekcan.txt",
    "seo":         "sang-woo_seo.txt",
    "kim":         "bruce_kim.txt",
    "baurin":      "edward_baurin.txt",
}

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
    where = None
    query_lower = query.lower()
    for last_name, filename in PROFESSOR_MAP.items():
        if last_name in query_lower:
            where = {"source": filename}
            break
    result = collection.query(query_embeddings=[vec], n_results=k, where=where)
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
            snippet = r["text"][:500]
            print(f"  {i}. [source: {r['source']}] (dist: {r['distance']:.4f})")
            print(f"     {snippet}")
