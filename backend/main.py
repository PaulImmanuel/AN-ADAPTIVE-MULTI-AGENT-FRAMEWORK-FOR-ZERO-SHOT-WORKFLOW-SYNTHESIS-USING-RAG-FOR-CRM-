import logging
import json
import sqlite3
import pandas as pd
import numpy as np
import requests
import faiss
import re
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

# --- 1. SETUP & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION (n8n) ---
# REPLACE THIS WITH YOUR REAL KEY
N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZGZmMDRiMy1hNGU3LTRhMzctODZiNi02YWE5YmU2ZTFlMGYiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY1NDQ5ODg2fQ.HCpa_STo2CMj5wGGaetPH2WwuuTLIcjGXeTAMwA-RiU" 
N8N_BASE_URL = "http://localhost:5678/api/v1"

# --- GLOBAL VARIABLES ---
app = FastAPI(title="GenCRM AI Backend")
embedding_model = None
kb_df = None          # Dashboard Knowledge
auto_df = None        # Automation Templates (The 6000+ list)
faiss_index = None    # Dashboard Index
auto_faiss_index = None # Automation Index

# --- 2. STARTUP: LOAD BRAINS ---
@app.on_event("startup")
async def startup_event():
    global embedding_model, kb_df, auto_df, faiss_index, auto_faiss_index
    
    logger.info("🧠 Loading AI Model...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 

    # --- BRAIN 1: DASHBOARD LAYOUTS (Restored) ---
    try:
        logger.info("📂 Loading Dashboard Knowledge...")
        kb_df = pd.read_csv("crm_knowledge_base.csv")
        embeddings = embedding_model.encode(kb_df['recommendation'].tolist(), convert_to_tensor=True)
        faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
        faiss_index.add(embeddings.cpu().numpy())
    except Exception as e:
        logger.error(f"❌ Dashboard KB Error: {e}")

    # --- BRAIN 2: AUTOMATION TEMPLATES (The New Engine) ---
    try:
        logger.info("📂 Loading Automation Library...")
        auto_df = pd.read_csv("automation_knowledge_base.csv")
        
        # We embed the 'intent' column (Filename + Description)
        auto_embeddings = embedding_model.encode(auto_df['intent'].tolist(), convert_to_tensor=True, show_progress_bar=True)
        
        auto_faiss_index = faiss.IndexFlatL2(auto_embeddings.shape[1])
        auto_faiss_index.add(auto_embeddings.cpu().numpy())
        logger.info(f"✅ Loaded the Automation Templates!") #{len(auto_df)}
    except Exception as e:
        logger.error(f"❌ Automation KB Error: {e}")

def trigger_webhook_test(webhook_path, payload_data):
    """
    Simulates the 'Call' to the webhook so the user doesn't have to wait.
    Uses the n8n 'Test' URL which listens when you click 'Execute' in UI.
    """
    # Note: 'webhook-test' is the URL n8n listens on when you are in the Editor UI
    test_url = f"http://localhost:5678/webhook-test/{webhook_path}"
    
    try:
        logger.info(f"📞 Auto-Calling Webhook: {test_url}")
        # We send the user's data (like 'Paul', 'Manager') to the workflow
        response = requests.post(test_url, json=payload_data)
        
        if response.status_code == 200:
            return "⚡ **Auto-Execution:** I successfully triggered the workflow!"
        else:
            return f"⚠️ Workflow created, but auto-trigger failed ({response.status_code}). Please click 'Execute' in n8n."
            
    except Exception as e:
        return f"⚠️ Auto-trigger error: {str(e)}"
# --- 3. HELPER FUNCTIONS ---

def find_dashboard_context(industry, goal, k=2):
    """Finds dashboard advice based on industry."""
    if kb_df is None: return "No knowledge base available."
    
    industry_df = kb_df[kb_df['industry'].str.lower() == industry.lower()]
    if industry_df.empty: return "No specific recommendations found."

    # Simple search within the filtered industry rows
    industry_embeddings = embedding_model.encode(industry_df['recommendation'].tolist())
    industry_index = faiss.IndexFlatL2(industry_embeddings.shape[1])
    industry_index.add(industry_embeddings)

    query_embedding = embedding_model.encode([f"CRM for {industry} focused on {goal}"])
    distances, indices = industry_index.search(query_embedding, k=k)
    
    context_lines = []
    for i in indices[0]:
        row = industry_df.iloc[i]
        line = f"- Recommendation: {row['recommendation']} (Widget Hint: {row.iloc[3]})"
        context_lines.append(line)
    return "\n".join(context_lines)

def find_best_template_candidates(user_message, k=3):
    """
    Returns the TOP 3 template candidates from the 6000+ library.
    """
    if auto_df is None: return []
    
    query_vector = embedding_model.encode([user_message])
    distances, indices = auto_faiss_index.search(query_vector, k=k)
    
    candidates = []
    for idx in indices[0]:
        if idx < len(auto_df):
            row = auto_df.iloc[idx]
            # We send the AI the "Intent" and the "ID" (Index)
            candidates.append(f"OPTION_ID: {idx} | DESCRIPTION: {row['intent']}")
            
    return candidates

INTERNAL_POSTGRES_CREDS = {
    "name": "Internal CRM Database",
    "type": "postgres",
    "data": {
        "user": "changeUser",
        "password": "changePassword",
        "database": "n8n",
        "host": "postgres",
        "port": 5432
    }
}
# --- ADD THIS HELPER FUNCTION BEFORE deploy_template_to_n8n ---
def fix_node_compatibility(nodes):
    """
    Modernizes old node types to match the latest n8n version.
    """
    # MAP: Old Name -> New Name
    replacements = {
        "n8n-nodes-base.openai": "n8n-nodes-base.openAi",
        "n8n-nodes-base.googleSheets": "n8n-nodes-base.googleSheets", # Usually fine, but good to be explicit
        "n8n-nodes-base.postgres": "n8n-nodes-base.postgres",
        "n8n-nodes-base.typeform": "n8n-nodes-base.typeform",
        # Add a generic fallback for capitalization issues if needed
    }

    fixed_nodes = []
    for node in nodes:
        current_type = node.get("type", "")
        
        # 1. Direct Replacement
        if current_type in replacements:
            node["type"] = replacements[current_type]
            
        # 2. Capitalization Fix (OpenAI -> openAi is the most common breaker)
        elif current_type.endswith(".openai"):
             node["type"] = current_type.replace(".openai", ".openAi")
             
        fixed_nodes.append(node)
        
    return fixed_nodes
def inject_internal_credentials(nodes):
    """
    Scans the workflow. If it sees a Database node, it injects OUR credentials.
    This removes the need for the user to configure it.
    """
    for node in nodes:
        # If the node is PostgreSQL, we attach our internal credential ID
        if "postgres" in node.get("type", "").lower():
            # In a real n8n API usage, we'd need to create the credential ID first.
            # For this demo, we assume a credential named "Postgres Local" exists in n8n.
            node["credentials"] = {"postgres": {"id": "1", "name": "Postgres Local"}}
            
    return nodes

def deploy_template_to_n8n(template_json_str):
    headers = {"X-N8N-API-KEY": N8N_API_KEY}
    
    try:
        data = json.loads(template_json_str)
        nodes = fix_node_compatibility(data.get('nodes', []))
        nodes = inject_internal_credentials(nodes)
        
        # EXTRACT WEBHOOK PATH (For Auto-Execution)
        webhook_path = None
        for node in nodes:
            if "webhook" in node.get("type", "").lower():
                # Look for the path parameter
                params = node.get("parameters", {})
                webhook_path = params.get("path")
                break

        payload = {
            "name": f"AI Gen: {data.get('name', 'Workflow')}",
            "nodes": nodes,
            "connections": data.get('connections', {}),
            "settings": data.get('settings', {})
        }

        # Clean forbidden keys
        for forbidden in ['active', 'id', 'tags', 'createdAt', 'updatedAt']:
            if forbidden in payload:
                del payload[forbidden]

        response = requests.post(f"{N8N_BASE_URL}/workflows", json=payload, headers=headers)
        
        if response.status_code == 200:
            wf_id = response.json().get('id')
            return True, wf_id, webhook_path, f"✅ Success! I deployed the **{payload['name']}** workflow (ID: {wf_id})."
        else:
            return False, None, None, f"❌ n8n Error: {response.text}"

    except Exception as e:
        return False, None, None, f"❌ System Error: {str(e)}"

# --- 4. API ENDPOINTS ---

origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class WizardData(BaseModel):
    company_name: str
    industry: str
    pipeline_stages: str
    contact_info: str
    primary_goal: str

class ChatRequest(BaseModel):
    message: str

# --- ENDPOINT 1: DASHBOARD GENERATION (Restored) ---
@app.post("/api/generate-dashboard")
async def generate_dashboard(data: WizardData):
    logger.info(f"Generating dashboard for: {data.industry}")
    
    # 1. Get Context
    relevant_context = find_dashboard_context(data.industry, data.primary_goal)
    
    # 2. Prompt for Dashboard Layout
    enhanced_prompt = f"""
    You are an expert CRM Solutions Architect. Your task is to generate a JSON configuration for a new CRM dashboard.
    **CRITICAL INSTRUCTION: You MUST STRICTLY ADHERE to the JSON schema.**

    --- CONTEXT ---
    {relevant_context}
    --- END CONTEXT ---
    
    **User Requirements:**
    - Industry: {data.industry}
    - Goal: {data.primary_goal}

    **REQUIRED JSON SCHEMA:**
    {{
      "dashboardTitle": "A string",
      "tabs": [
        {{
          "title": "A string",
          "widgets": [ {{ "type": "MUST be 'StatusChart', 'RecentTicketsTable', 'MetricCard', or 'LeadsBarChart'" }} ]
        }}
      ]
    }}
    
    Generate JSON only.
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gpt-oss:120b-cloud", "prompt": enhanced_prompt, "format": "json", "stream": False}
        )
        final_config = json.loads(response.json()['response'])
        return {"status": "success", "config": final_config}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

# --- ENDPOINT 2: CHAT AUTOMATION (The New Engine) ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Chat: {request.message}")
    
    # 1. SEARCH
    candidates = find_best_template_candidates(request.message)
    candidates_str = "\n".join(candidates)
    
    # 2. SELECT
    system_prompt = f"""
    You are an Expert Automation Architect.
    User Request: "{request.message}"
    
    Here are the matching templates:
    {candidates_str}
    
    INSTRUCTIONS:
    1. Select the ONE Option ID that best matches.
    2. Extract KEY INFORMATION from the user request (Name, Role, Industry, etc).
    3. Return JSON with 'selected_id' and 'extracted_data'.
    
    Example Output:
    {{ 
      "selected_id": 0, 
      "reason": "User wants to create account",
      "extracted_data": {{ "name": "Paul", "role": "Manager" }}
    }}
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1", "prompt": system_prompt, "format": "json", "stream": False}
        )
        ai_response_json = json.loads(response.json()['response'])
        
        selected_id = int(ai_response_json.get('selected_id', -1))
        reason = ai_response_json.get('reason', 'Best match found.')
        user_data = ai_response_json.get('extracted_data', {})
        
        # 3. DEPLOY & EXECUTE
        if selected_id >= 0 and auto_df is not None:
            full_template_json = auto_df.iloc[selected_id]['json_template']
            
            # Deploy
            success, wf_id, webhook_path, status_msg = deploy_template_to_n8n(full_template_json)
            
            final_reply = f"{status_msg}\n\n**Strategy:** {reason}"
            
            # AUTO-EXECUTE LOGIC
            if success and webhook_path:
                final_reply += "\n\n🔄 **Auto-Triggering Workflow...**"
                # We need to give n8n a split second to register the webhook
                import time
                time.sleep(1) 
                
                # NOTE: In a real app, you would hit the production webhook. 
                # For this demo, we assume the user might have clicked 'Execute' to watch it,
                # OR we send it to the production URL if active.
                # Since we can't activate via API easily, we will print the Test URL for them.
                
                test_url = f"http://localhost:5678/webhook-test/{webhook_path}"
                final_reply += f"\n👉 [Click here to Auto-Run]({test_url}) (or I can try to trigger it automatically if n8n is listening)."
                
                # Try to trigger it automatically
                trigger_msg = trigger_webhook_test(webhook_path, user_data)
                final_reply += f"\n{trigger_msg}"

            return {"response": final_reply}
            
        else:
            return {"response": "I couldn't find a suitable template."}

    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return {"response": f"I encountered a system error: {str(e)}"}
    
# --- ENDPOINT 3: DUMMY DATA FOR CHARTS (Restored) ---
@app.get("/api/metrics/revenue")
async def get_revenue_metrics():
    return {"total_revenue": "$124,500", "growth": "+12%", "active_users": "1,240", "churn_rate": "2.4%"}

@app.get("/api/leads/sources")
async def get_lead_sources():
    return {"labels": ["LinkedIn", "Google Ads", "Referrals", "Cold Email"], "data": [45, 120, 30, 15]}

@app.get("/api/tickets/status-overview")
async def get_ticket_status_overview():
    # Returning dummy data so it works without DB for now
    return [{"ticket_status": "Open", "count": 12}, {"ticket_status": "Closed", "count": 45}]

@app.get("/api/tickets/recent")
async def get_recent_tickets():
    return [{"customer_name": "Alice", "ticket_subject": "Login Issue", "ticket_status": "Open", "ticket_priority": "High"}]

# --- RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)