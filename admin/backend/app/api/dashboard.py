from fastapi import APIRouter

router = APIRouter(tags=["dashboard"])

@router.get("/")
def get_dashboard():
    return {"message": "Dashboard data"}