from fastapi import File, UploadFile
from ..models import HTTP500InternalServerError


async def upload(uploaded_file: UploadFile = File(...)):
    return HTTP500InternalServerError(detail="Not implemented yet.")
