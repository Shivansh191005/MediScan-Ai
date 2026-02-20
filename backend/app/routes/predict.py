from fastapi import APIRouter, UploadFile, File
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from groq import Groq
from app.services.yolo_service import predict_ultrasound
from app.services.report_service import generate_pdf
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter()

@router.post("/predict-image")
async def predict_image(file: UploadFile = File(...)):

    image_path = f"temp_{file.filename}"

    with open(image_path, "wb") as f:
        f.write(await file.read())

    findings, annotated_path = await run_in_threadpool(
        predict_ultrasound,
        image_path
    )

    prompt = f"""
Explain ultrasound findings clearly.

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

    explanation = completion.choices[0].message.content

    pdf_file = generate_pdf(findings, explanation, annotated_path)

    return {
        "raw_findings": findings,
        "explanation": explanation,
        "image_url": f"/image/{annotated_path}",
        "pdf_url": f"/report/{pdf_file}"
    }


@router.get("/image/{filename}")
def get_image(filename: str):
    return FileResponse(filename)


@router.get("/report/{filename}")
def get_report(filename: str):
    return FileResponse(filename, media_type="application/pdf")
