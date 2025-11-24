import chromadb

# 1. Connect to the existing DB
DB_PATH = "./leetcodedb_data"
client = chromadb.PersistentClient(path=DB_PATH)

try:
    collection = client.get_collection(name="leetcode_solutions")
    count = collection.count()
    print(f"--- DATABASE INSPECTION ---")
    print(f"Total Records Found: {count}")
    
    if count == 0:
        print("⚠️ Database is empty! Run build_db.py again.")
    else:
        # 2. Fetch first 50 items (ID and Metadata)
        print("\n--- SAMPLE TITLES (First 50) ---")
        data = collection.get(limit=50, include=["metadatas"])
        
        for idx, meta in enumerate(data["metadatas"]):
            # Print the 'name' field we saved earlier
            title = meta.get("name", "UNKNOWN_TITLE")
            print(f"{idx+1}. {title}")

        print("\n" + "="*40)
        print("DIAGNOSIS:")
        print("1. Are these titles readable? (e.g. 'Two Sum' vs 'two-sum' vs 'problem_1')")
        print("2. If they look like 'problem_description', our search is trying to match")
        print("   a short title against a long paragraph, which fails.")
        print("="*40)

except Exception as e:
    print(f"❌ Error accessing database: {e}")
    print("Did you run build_db.py first?")