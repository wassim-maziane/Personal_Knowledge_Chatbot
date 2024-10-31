from fastapi import Cookie, FastAPI, UploadFile, Depends, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db_utils import get_chat_history, insert_chat_log
from app.langchain_utils import get_chain, get_retriever
from app.models import QueryResponse
from app.qdrant import index_doc_to_qdrant
from app.utils import validate_file_type
import uuid
import shutil
import os
from typing import Annotated
import logging

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Personal-Knowledge-Chatbot"
os.environ["LANGCHAIN_API_KEY"] = ".."

logging.basicConfig(filename="app.log", level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chat")
async def chat(question: str, session_id: Annotated[str, Cookie()]):
    logging.info(f"Session ID: ${session_id}, User Query: ${question}")
    retriever = get_retriever(session_id)
    rag_chain = get_chain(retriever)
    chat_history = get_chat_history(session_id)
    answer = rag_chain.invoke({"input": question, "chat_history": chat_history})[
        "answer"
    ]
    insert_chat_log(session_id, question, answer, "llama3.1:8b")
    logging.info(f"Session ID: ${session_id}, AI Answer: ${answer}")
    return QueryResponse(answer=answer, session_id=session_id)


@app.post("/upload-doc")
async def upload_document(
    response: Response,
    session_id: Annotated[str | None, Cookie()] = None,
    file: UploadFile = Depends(validate_file_type),
):
    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)
        logging.info(f"Created new session ID: {session_id}")
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        success = index_doc_to_qdrant(temp_file_path, session_id)
        if success:
            return {
                "message": f"File {file.filename} has beend successfully uploded and indexed",
                "session_id": session_id,
            }
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to index document {file.filename}"
            )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
