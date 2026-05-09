from fastapi import FastAPI, HTTPException, Header
from supabase import create_client
import requests
import os
import secrets

app = FastAPI()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def root():
    return {"status": "Glitch AI is running! 🔮"}

@app.post("/generate-key")
async def generate_key(email: str):
    new_key = "gk-" + secrets.token_urlsafe(32)
    supabase.table("api_keys").insert({
        "key": new_key,
        "user_email": email,
        "is_active": True
    }).execute()
    return {"api_key": new_key}

@app.post("/chat")
async def chat(message: str, authorization: str = Header(None)):
    result = supabase.table("api_keys").select("*").eq("key", authorization).eq("is_active", True).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    prompt = f"""You are Glitch. Examples:

User: yo
Assistant: yo what's good

User: what are you  
Assistant: just an ai thing talking to you

User: are you smart
Assistant: kinda, depends what you ask

User: whats 2+2
Assistant: 4 obviously

Now respond (SHORT, 1-2 sentences):
User: {message}
Assistant:"""
    
    response = requests.post(
        "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 100}}
    )
    
    ai_response = response.json()[0]["generated_text"].split("Assistant:")[-1].strip()
    return {"response": ai_response}
