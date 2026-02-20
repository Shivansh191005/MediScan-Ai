from fastapi import APIRouter, UploadFile, File
from app.services.rag_service import ingest_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    ingest_pdf(file_path)

    return {"status": "Document stored successfully"}
