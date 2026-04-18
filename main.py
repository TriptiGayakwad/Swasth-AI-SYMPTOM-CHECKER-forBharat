import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

# Enable CORS so your HTML file can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq Client (Get your key from console.groq.com)
client = Groq(api_key="YOUR_GROQ_API_KEY")

class SymptomRequest(BaseModel):
    text: str
    lang: str

@app.post("/analyze")
async def analyze_symptoms(request: SymptomRequest):
    # The Prompt: Instructs the AI to be a triage assistant and return JSON
    system_prompt = f"""
    You are a medical triage assistant for rural Bharat. 
    Analyze the symptoms provided in {request.lang}. 
    Return ONLY a JSON object with this exact structure:
    {{
        "conditions": [
            {{ "name": "Condition Name", "risk": "Low/Medium/High", "color": "teal/amber/red" }}
        ],
        "advice": "3 short bullet points of advice in {request.lang}"
    }}
    Important: Do not provide a diagnosis. Provide triage risk assessment.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {{"role": "system", "content": system_prompt}},
            {{"role": "user", "content": request.text}}
        ],
        model="llama3-8b-8192", # Lightweight and fast for hackathons
        response_format={{"type": "json_object"}} # Ensures valid JSON
    )

    return chat_completion.choices[0].message.content