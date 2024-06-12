# main.py (FastAPI Backend)
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import PyPDF2
import datetime
from database import SessionLocal, engine, Base, Document as DB_Document
from transformers import pipeline

app = FastAPI()

# Create the upload directory if it doesn't exist
UPLOAD_DIR = "./docs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

#model
qa_model = pipeline("question-answering")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model for receiving question
class Question(BaseModel):
    question: str
    documentId: int

# Model for sending answer
class Answer(BaseModel):
    answer: str

class DocumentId(BaseModel):
    documentId: int

# Endpoint for uploading PDF documents
@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Save the document details to the database
    db_document = DB_Document(
        filename=file.filename,
        upload_date=datetime.datetime.utcnow(),
        file_path=file_path
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return {"id": db_document.id, "filename": db_document.filename, "upload_date": db_document.upload_date}

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        pdf_reader = PyPDF2.PdfReader(f) # Use PdfReader from PyPDF2
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() # Use extract_text() to get text from the page object
        return text

# Endpoint for receiving questions and returning answers
@app.post("/ask/", response_model=Answer)
async def ask_question(que: Question):
    try:
        db = SessionLocal()
        # Fetch the document from the database using documentId
        db_document = db.query(DB_Document).filter(DB_Document.id == que.documentId).first()
        if db_document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        # Use the text content from the document for NLP processing
        file_path = db_document.file_path
        context = extract_text_from_pdf(file_path)
        question = str(que.question)

        # test model
        qa_response = qa_model(question = question, context = context)


        # Analyze the question and generate an appropriate answer
        # answer = generate_answer(que.question, text_content)
        return {"answer": qa_response['answer']}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Oops! Something went wrong.")
