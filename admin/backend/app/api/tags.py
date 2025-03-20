from fastapi import APIRouter

router = APIRouter(
    tags=["tags"]
)

@router.get("/")
def get_tags():
    return {"message": "List tags"}