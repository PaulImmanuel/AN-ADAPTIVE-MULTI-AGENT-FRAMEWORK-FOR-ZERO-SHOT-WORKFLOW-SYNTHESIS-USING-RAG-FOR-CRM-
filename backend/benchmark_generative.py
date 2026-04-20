import requests
import json
import time

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"
SAMPLE_SIZE = 10  # Keep it small for speed, or 50 for accuracy

# Simple prompts to test generation
TEST_PROMPTS = [
    "Create an n8n workflow to sync Slack messages to Google Sheets.",
    "Create a workflow that sends an email when a Webhook is triggered.",
    "Generate a workflow to scrape a website and save to Postgres.",
    "Make an n8n automation that watches Gmail and posts to Discord.",
    "Create a workflow to backup Trello cards to Airtable."
]

def benchmark_generative_approach():
    print(f"🧪 BENCHMARKING GENERATIVE APPROACH ({SAMPLE_SIZE} iterations)...")
    print("---------------------------------------------------------------")
    
    valid_count = 0
    syntax_errors = 0
    structure_errors = 0
    
    for i in range(SAMPLE_SIZE):
        prompt_text = TEST_PROMPTS[i % len(TEST_PROMPTS)]
        print(f"🤖 Attempt {i+1}: Asking LLM to '{prompt_text}'...")
        
        payload = {
            "model": MODEL_NAME,
            "prompt": f"Generate a valid JSON for an n8n workflow that does this: {prompt_text}. ONLY return the JSON.",
            "stream": False,
            "format": "json" # We give it a fighting chance by forcing JSON mode
        }
        
        try:
            start_time = time.time()
            response = requests.post(OLLAMA_URL, json=payload)
            latency = time.time() - start_time
            
            result_text = response.json()['response']
            
            # --- VALIDATION CHECKS ---
            try:
                # Check 1: Is it valid JSON?
                data = json.loads(result_text)
                
                # Check 2: Does it have the n8n structure?
                # Generative models often forget "nodes" or "connections" keys
                if "nodes" in data and "connections" in data:
                    # Check 3: Are nodes a list? (Common hallucination: nodes is a dict)
                    if isinstance(data['nodes'], list):
                        valid_count += 1
                        print(f"   ✅ Success ({latency:.2f}s)")
                    else:
                        print(f"   ❌ Failed: 'nodes' is not a list")
                        structure_errors += 1
                else:
                    print(f"   ❌ Failed: Missing 'nodes' or 'connections' keys")
                    structure_errors += 1
                    
            except json.JSONDecodeError:
                print(f"   ❌ Failed: Invalid JSON Syntax")
                syntax_errors += 1
                
        except Exception as e:
            print(f"   ⚠️ Request Error: {e}")

    # --- FINAL SCORE ---
    success_rate = (valid_count / SAMPLE_SIZE) * 100
    
    print("\n📊 --- GENERATIVE RESULTS ---")
    print(f"✅ Valid Workflows: {valid_count}/{SAMPLE_SIZE}")
    print(f"❌ Syntax Errors: {syntax_errors}")
    print(f"❌ Structure Errors: {structure_errors}")
    print("-------------------------------")
    print(f"📉 GENERATIVE RELIABILITY SCORE: {success_rate:.2f}%")
    print("-------------------------------")
    
    return success_rate

if __name__ == "__main__":
    benchmark_generative_approach()