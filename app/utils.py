from fastapi import HTTPException, UploadFile, File
import os


ALLOWED_EXTENSIONS = [".pdf", ".docx", ".html"]


def validate_file_type(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is necessary")
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File must be of type {', '.join(ALLOWED_EXTENSIONS)} ",
        )
    return file
