from fastapi import APIRouter

router = APIRouter(
    tags=["categories"]
)

@router.get("/")
def get_categories():
    return {"message": "List categories"}