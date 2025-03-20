from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/")
async def upload_file():
    return {"message": "Upload file"}