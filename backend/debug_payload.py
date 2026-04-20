import requests
import json

# --- CONFIGURATION ---
# REPLACE WITH YOUR REAL KEY
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZGZmMDRiMy1hNGU3LTRhMzctODZiNi02YWE5YmU2ZTFlMGYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1NDQ5ODg2fQ.HCpa_STo2CMj5wGGaetPH2WwuuTLIcjGXeTAMwA-RiU" 
N8N_URL = "http://localhost:5678/api/v1/workflows"

# --- THE EXACT JSON YOU PROVIDED ---
raw_template = """
{
  "name": "ai-receptionist-lead-qualification",
  "nodes": [
    {
      "parameters": { "httpMethod": "POST", "path": "ai-receptionist-lead" },
      "id": "1",
      "name": "Lead Input Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [ 100, 300 ],
      "webhookId": "ai-receptionist-lead-input"
    },
    {
      "parameters": { "model": "gpt-4", "messages": [] },
      "id": "3",
      "name": "Qualify Lead (GPT-4)",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "position": [ 500, 300 ]
    }
  ],
  "connections": {},
  "active": false
}
"""

def debug_deploy():
    print("1. Parsing Raw Template...")
    data = json.loads(raw_template)
    
    # --- THE SANITIZATION LOGIC ---
    print("2. Constructing Clean Payload...")
    payload = {
        "name": "DEBUG TEST: " + data.get('name', 'Untitled'),
        "nodes": data.get('nodes', []),
        "connections": data.get('connections', {}),
        "settings": data.get('settings', {}),
        "tags": []
    }
    
    # 🕵️‍♂️ PARANOID CHECK: Check if 'active' somehow snuck in
    if 'active' in payload:
        print("⚠️ ALARM: 'active' key found in payload! Deleting it.")
        del payload['active']
    else:
        print("✅ Check passed: No 'active' key in payload.")

    # Print the keys we are sending
    print(f"3. Sending Payload with keys: {list(payload.keys())}")
    
    headers = {"X-N8N-API-KEY": N8N_API_KEY}
    
    try:
        response = requests.post(N8N_URL, json=payload, headers=headers)
        print(f"4. Response Code: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! Workflow created.")
            print(f"ID: {response.json().get('id')}")
        else:
            print(f"❌ ERROR: {response.text}")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}")

if __name__ == "__main__":
    debug_deploy()