import chromadb
from sentence_transformers import SentenceTransformer

print("   [Search Engine] Loading Model & DB...")
client = chromadb.PersistentClient(path="./leetcodedb_data")
collection = client.get_collection(name="leetcode_solutions")
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_solution(user_code, predicted_slug=None):
    """
    Priority 1: Exact Metadata Match on Slug (100% Accuracy).
    Priority 2: Vector Search on Code Logic (Fallback).
    """
    
    # STRATEGY 1: EXACT METADATA LOOKUP (The "Direct Hit")
    if predicted_slug:
        print(f"   [search] 🔍 Attempting Direct Lookup for slug: '{predicted_slug}'...")
        
        # ChromaDB filter query
        direct_hit = collection.get(
            where={"name": predicted_slug},
            limit=1,
            include=["documents", "metadatas"]
        )
        
        if direct_hit['ids']:
            print(f"   [search] 🎯 SUCCESS: Exact match found for '{predicted_slug}'!")
            return direct_hit['documents'][0], 1.0

    # STRATEGY 2: VECTOR SEARCH (Fallback)
    print(f"   [search] ⚠️ Direct lookup failed. Falling back to Vector Search...")
    query_vector = model.encode(user_code).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=1 
    )
    
    if not results['documents'][0]:
        return None, 0.0
        
    best_code = results['documents'][0][0]
    confidence = 1 - results['distances'][0][0]
    
    return best_code, confidence

# This only runs if you run 'py search_engine.py' directly
if __name__ == "__main__":
    print("Testing Search Engine...")
    code, conf = find_solution("def test(): pass")
    print(f"Test Result: {conf}")