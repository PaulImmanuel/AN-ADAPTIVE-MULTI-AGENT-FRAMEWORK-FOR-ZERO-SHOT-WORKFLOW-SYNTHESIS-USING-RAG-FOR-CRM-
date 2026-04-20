import requests
import json

# REPLACE WITH YOUR KEY
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZGZmMDRiMy1hNGU3LTRhMzctODZiNi02YWE5YmU2ZTFlMGYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1NDQ5ODg2fQ.HCpa_STo2CMj5wGGaetPH2WwuuTLIcjGXeTAMwA-RiU"
URL = "http://localhost:5678/api/v1/workflows"

headers = {"X-N8N-API-KEY": API_KEY}

# We will try to create a simple workflow with valid lowercase types
payload = {
    "name": "Debug Test Workflow",
    "nodes": [
        {
            "parameters": {},
            "name": "Start",
            "type": "n8n-nodes-base.manualTrigger", # Lowercase is safer
            "typeVersion": 1,
            "position": [250, 300]
        },
        {
            "parameters": {
                "channel": "#general",
                "text": "Debug Test"
            },
            "name": "Slack",
            "type": "n8n-nodes-base.slack", # Lowercase 'slack'
            "typeVersion": 1,
            "position": [450, 300]
        }
    ],
    "connections": {
        "Start": {
            "main": [
                [
                    {
                        "node": "Slack",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

print("Sending request to n8n...")
response = requests.post(URL, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")