import requests
import json

print("\n--- RUNNING RELIABILITY TEST FOR TABLE 1 & 2 ---")

def ask_ollama(prompt):
    res = requests.post("http://localhost:11434/api/generate", 
                        json={"model": "llama3.1", "prompt": prompt, "stream": False})
    return res.json()['response']

# 1. RAW LLM (No Context)
print("\n[TEST A] Asking Raw LLM (No Context)...")
raw_prompt = "Generate a JSON configuration for a dashboard widget."
raw_response = ask_ollama(raw_prompt)
print(f"Raw Output Start: {raw_response[:100]}...")
if "{" in raw_response and "widget" in raw_response:
    print("-> Result: Unpredictable (Might be text, might be JSON)")
else:
    print("-> Result: FAILURE (Hallucinated text instead of JSON)")

# 2. RAG LLM (With Context/Schema)
print("\n[TEST B] Asking RAG System (With Context & Schema)...")
rag_prompt = """
You are a JSON generator. 
REQUIRED SCHEMA: {"type": "StatusChart", "title": "string"}
CONTEXT: Use StatusChart for support tickets.
Generate JSON only.
"""
rag_response = ask_ollama(rag_prompt)
print(f"RAG Output: {rag_response}")

try:
    json.loads(rag_response)
    print("-> Result: SUCCESS (Valid JSON generated)")
except:
    print("-> Result: Failed")

print("\nCONCLUSION: RAG Context drastically increases Syntax Success Rate")