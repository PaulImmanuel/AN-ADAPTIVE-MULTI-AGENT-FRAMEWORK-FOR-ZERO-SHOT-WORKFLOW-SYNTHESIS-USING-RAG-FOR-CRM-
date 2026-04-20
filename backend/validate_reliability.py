import pandas as pd
import json
import random

# --- CONFIGURATION ---
CSV_PATH = "automation_knowledge_base.csv"

def check_template_validity():
    print("🧪 STARTING RELIABILITY BENCHMARK...")
    
    try:
        df = pd.read_csv(CSV_PATH)
        total = len(df)
        print(f"📂 Loaded {total} templates from Knowledge Base.")
        
        valid_count = 0
        syntax_errors = 0
        structure_errors = 0
        
        # We test a random sample of 500 to be statistically significant
        # (Or test all of them if you want, it takes a few seconds)
        sample_size = min(total, 500)
        sample = df.sample(n=sample_size)
        
        print(f"🔍 Testing {sample_size} random templates...")

        for index, row in sample.iterrows():
            json_str = row['json_template']
            
            try:
                # TEST 1: IS IT VALID JSON?
                data = json.loads(json_str)
                
                # TEST 2: DOES IT HAVE THE REQUIRED FIELDS?
                if "nodes" in data and "connections" in data:
                    valid_count += 1
                else:
                    structure_errors += 1
                    
            except json.JSONDecodeError:
                syntax_errors += 1

        # --- CALCULATE SCORES ---
        success_rate = (valid_count / sample_size) * 100
        
        print("\n📊 --- RESULTS ---")
        print(f"✅ Successful Templates: {valid_count}")
        print(f"❌ Syntax Errors: {syntax_errors}")
        print(f"❌ Structure Errors: {structure_errors}")
        print("-------------------------------")
        print(f"🏆 TEMPLATE RELIABILITY SCORE: {success_rate:.2f}%")
        print("-------------------------------")
        
        return success_rate

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return 0

if __name__ == "__main__":
    score = check_template_validity()