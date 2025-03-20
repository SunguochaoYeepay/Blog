from fastapi import APIRouter

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/")
async def get_comments():
    return {"message": "List comments"}