from fastapi import APIRouter
from pydantic import BaseModel
from groq import Groq
from app.services.rag_service import search_docs
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter()
chat_memory = []

class Message(BaseModel):
    message: str

@router.post("/chat")
def chat(msg: Message):

    context = search_docs(msg.message)

    if context.strip() == "":
        return {"reply": "Please upload a document first."}

    prompt = f"""
You are a document question answering assistant.

Use the conversation history and document context.

Document Context:
{context}

User Question:
{msg.message}
"""

    chat_memory.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_memory
    )

    reply = completion.choices[0].message.content
    chat_memory.append({"role": "assistant", "content": reply})

    return {"reply": reply}
