import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./leetcodedb_data")
collection = client.get_collection(name="leetcode_solutions")
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_solution(user_code, predicted_name=None):
    # STRATEGY: Hybrid Search
    # We combine the User's Code Logic + The AI's Prediction into one strong query vector.
    
    if predicted_name:
        print(f"   [search] 🔍 Boosting search with prediction: '{predicted_name}'")
        # We weigh the prediction heavily so it pulls us to the right topic
        search_query = f"{predicted_name} {predicted_name} {user_code[:200]}"
    else:
        search_query = user_code

    query_vector = model.encode(search_query).tolist()
    
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