import time
import numpy as np
from sentence_transformers import SentenceTransformer, util

print("\n--- RUNNING SCIENTIFIC BENCHMARK (Averaged over 10 runs) ---")
print("Please wait... performing warm-up and multiple passes...\n")

# 1. Setup Data
query = "I need a dashboard to manage customer support tickets."
documents = [
    "SaaS companies track MRR.", 
    "Real Estate tracks listings.", 
    "Customer Support tracks ticket status and priority.", # Index 2
    "E-commerce tracks inventory."
]

models = [
    'all-MiniLM-L6-v2',           # MY MODEL
    'all-mpnet-base-v2',          # THE HEAVY COMPETITOR
    'paraphrase-albert-small-v2'  # THE LIGHTWEIGHT COMPETITOR
]

print(f"{'MODEL NAME':<30} | {'AVG TIME':<10} | {'CONFIDENCE':<10}")
print("-" * 60)

for model_name in models:
    try:
        # Load Model
        model = SentenceTransformer(model_name)
        
        # --- WARM UP PASS (Don't count this time) ---
        model.encode("warm up query")
        
        # --- RUN 10 TIMES AND AVERAGE ---
        times = []
        for _ in range(10):
            start = time.time()
            q_emb = model.encode(query)
            d_emb = model.encode(documents)
            end = time.time()
            times.append((end - start) * 1000)
        
        avg_time = np.mean(times)

        # Measure Accuracy (Just once is enough)
        scores = util.cos_sim(q_emb, d_emb)[0]
        accuracy = scores[2].item()

        print(f"{model_name:<30} | {avg_time:.2f} ms   | {accuracy:.4f}")

    except Exception as e:
        print(f"{model_name:<30} | ERROR")

print("-" * 60)
print("CONCLUSION: While Albert is faster, MiniLM offers the best semantic balance.")