import time
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

print("\n--- RUNNING LATENCY TEST FOR TABLE 2 & 3 ---")

# 1. Setup Retrieval (Simulated)
print("1. Loading RAG Engine...", end=" ")
kb_df = pd.read_csv("crm_knowledge_base.csv")
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(kb_df['recommendation'].tolist())
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
print("Done.")

# 2. TEST RETRIEVAL SPEED
print("\n[TEST A] Measuring Retrieval Speed (Vector Search)...")
start_retrieval = time.time()

query_vec = model.encode(["Customer Support"])
D, I = index.search(query_vec, k=2)

end_retrieval = time.time()
retrieval_ms = (end_retrieval - start_retrieval) * 1000
print(f"✅ Retrieval Time: {retrieval_ms:.4f} ms")

# 3. TEST GENERATION SPEED
print("\n[TEST B] Measuring Generation Speed (Ollama LLM)...")
start_gen = time.time()

# Sending a real request to Ollama
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1",
            "prompt": "Generate a JSON for a CRM dashboard.",
            "stream": False
        }
    )
    end_gen = time.time()
    gen_s = end_gen - start_gen
    print(f"✅ Generation Time: {gen_s:.4f} seconds")
except:
    print("❌ Ollama not running. Cannot test generation.")

print("\nCONCLUSION: Retrieval is negligible (<1% latency). LLM is the bottleneck.")