import os
from fastapi import HTTPException
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


def validate_file(filename: str, file_size: int):
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10 MB."
        )

    return True
