import os
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

# --- CONFIGURATION ---
# UPDATE THIS PATH to where you extracted the files
# BASE_PATH = r"D:/Karunya/4th Year/Final-Year-Project/Main_Project/CRM/n8n-automation-templates" 
BASE_PATH = r"D:/Karunya/4th Year/Final-Year-Project/Main_Project/CRM/backend/core_workflows"

# We prioritize these folders because they have the "Smart" workflows
PRIORITY_FOLDERS = [
    "n8n advance",
    "workflows by Zie619" 
]

OUTPUT_CSV = "automation_knowledge_base.csv"
MODEL_NAME = 'all-MiniLM-L6-v2'

def clean_filename(filename):
    """Converts 'auto-save-to-slack.json' -> 'Auto Save To Slack'"""
    name = filename.replace('.json', '').replace('-', ' ').replace('_', ' ')
    return name.title()

def load_templates():
    templates = []
    
    print(f"📂 Scanning directories in {BASE_PATH}...")

    for root, dirs, files in os.walk(BASE_PATH):
        folder_name = os.path.basename(root)
        
        # Check if we should process this folder
        # We process everything, but we can tag priority later if needed
        
        for file in files:
            if file.endswith(".json") and file != "metadata.json":
                full_path = os.path.join(root, file)
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract valuable info
                    workflow_name = data.get('name', clean_filename(file))
                    
                    # Store the RAW JSON string to give to n8n later
                    # We minify it to save CSV space
                    json_str = json.dumps(data)
                    
                    # Create the "Intent" string for the AI to search
                    # e.g., "Analyze Sales Call Transcripts (n8n advance)"
                    intent_desc = f"{workflow_name} - {folder_name}"
                    
                    templates.append({
                        "intent": intent_desc,
                        "tool": "n8n Workflow",
                        "json_template": json_str,
                        "category": folder_name
                    })
                    
                except Exception as e:
                    # Skip broken files
                    pass

    print(f"✅ Found {len(templates)} valid workflow templates.")
    return templates

def build_vector_db(templates):
    print("🧠 Loading AI Model for Embedding...")
    model = SentenceTransformer(MODEL_NAME)
    
    df = pd.DataFrame(templates)
    
    print("⚡ Creating Embeddings (This may take a minute)...")
    embeddings = model.encode(df['intent'].tolist(), show_progress_bar=True)
    
    # Save CSV
    print(f"💾 Saving {OUTPUT_CSV}...")
    df.to_csv(OUTPUT_CSV, index=False)
    
    # We don't save the FAISS index here, we let main.py rebuild it on startup
    # to keep things simple.
    print("✅ Knowledge Base Built Successfully!")

if __name__ == "__main__":
    if not os.path.exists(BASE_PATH):
        print(f"❌ Error: Path not found: {BASE_PATH}")
        print("Please edit the BASE_PATH variable in the script.")
    else:
        data = load_templates()
        if data:
            build_vector_db(data)