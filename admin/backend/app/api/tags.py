from fastapi import APIRouter

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/")
async def get_tags():
    return {"message": "List tags"}