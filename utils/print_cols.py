from datasets import load_dataset

print("Downloading one sample from dataset...")
dataset = load_dataset("newfacade/LeetCodeDataset", split="train", streaming=True)
sample = next(iter(dataset))

print("\n--- DATASET COLUMNS ---")
print(sample.keys())
print("-" * 30)
print("SAMPLE CONTENT (First 100 chars):")
print(str(sample)[:200])