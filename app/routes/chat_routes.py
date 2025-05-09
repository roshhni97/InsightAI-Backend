from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.rag_service import ask_question
from app.services.pdf_service import process_pdf
from pydantic import BaseModel
import shutil
import os

router = APIRouter()

# Create tmp directory if it doesn't exist
os.makedirs("./tmp", exist_ok=True)

class QuestionRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask(request: QuestionRequest):
    print(request.query)
    return {"response": ask_question(request.query)}

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
            
        file_path = f"./tmp/{file.filename}"
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF
        result = process_pdf(file_path)
        print(file)
        return {
            "status": "success", 
            "message": "PDF processed successfully",
            "filename": file.filename,
            "summary": result["summary"],
            "key_topics": result["key_topics"],
            "document_structure": result["document_structure"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
