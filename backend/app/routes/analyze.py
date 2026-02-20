from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter()

class Message(BaseModel):
    message: str

@router.post("/analyze")
def analyze_findings(msg: Message):

    findings = msg.message

    prompt = f"""
You are a medical assistant explaining ultrasound findings.

Findings:
{findings}

Explain:
- What it means
- Is it dangerous?
- What to do next
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = completion.choices[0].message.content
    return {"reply": reply}
