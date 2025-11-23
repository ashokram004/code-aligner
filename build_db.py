import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from tqdm import tqdm
import shutil
import os

# --- CONFIGURATION ---
DB_PATH = "./leetcodedb_data"
MODEL_NAME = 'all-MiniLM-L6-v2'
BATCH_SIZE = 50 

def build_database():
    print("--- 1. CLEANING UP OLD DATA ---")
    if os.path.exists(DB_PATH):
        try:
            shutil.rmtree(DB_PATH)
            print("Deleted old database folder.")
        except Exception as e:
            print(f"Warning: Could not delete folder (might be in use). Error: {e}")

    # Initialize New DB
    chroma_client = chromadb.PersistentClient(path=DB_PATH)
    collection = chroma_client.get_or_create_collection(name="leetcode_solutions")
    print(f"New Database initialized at: {DB_PATH}")

    print("\n--- 2. LOADING AI MODELS & DATA ---")
    model = SentenceTransformer(MODEL_NAME)
    
    # Load dataset
    print("Downloading LeetCode Dataset...")
    dataset = load_dataset("newfacade/LeetCodeDataset", split="train")
    
    total_records = len(dataset)
    print(f"Dataset Loaded. Total Problems: {total_records}")

    print("\n--- 3. INGESTION STARTED (Using 'completion' column) ---")
    
    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for i, row in tqdm(enumerate(dataset), total=total_records):
        
        # --- THE FIX IS HERE ---
        # We use 'completion' which contains the full solution code
        code_solution = row.get('completion', '')
        
        # Fallback: Sometimes 'completion' is None, check 'response'
        if not code_solution:
            code_solution = row.get('response', '')

        if not code_solution:
            continue

        # Create Embedding
        vector = model.encode(code_solution).tolist()
        
        # Get problem name (or make one up)
        p_name = row.get('task_id', f"Problem {i}")

        ids.append(str(i))
        embeddings.append(vector)
        # Store metadata
        metadatas.append({"id": i, "name": p_name})
        # Store the actual code text
        documents.append(code_solution)

        # Batch Insert
        if len(ids) >= BATCH_SIZE:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            ids, embeddings, metadatas, documents = [], [], [], []

    # Final Batch
    if ids:
        collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    print("\n" + "="*50)
    print(f"SUCCESS! Database built with {collection.count()} problems.")
    print("="*50)

if __name__ == "__main__":
    build_database()