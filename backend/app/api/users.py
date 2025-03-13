from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..schemas.user import UserResponse, UserQuery
from ..models.user import User
from ..database import get_db
from sqlalchemy import or_
from ..logger import setup_logger

# 创建用户模块的日志记录器
logger = setup_logger("users")

router = APIRouter()

@router.get("/users/", response_model=List[UserResponse])
async def search_users(
    query: UserQuery = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"Searching users with query: {query}, skip: {skip}, limit: {limit}")
    
    filters = []
    if query.username:
        filters.append(User.username.ilike(f"%{query.username}%"))
    if query.email:
        filters.append(User.email.ilike(f"%{query.email}%"))
    if query.department:
        filters.append(User.department.ilike(f"%{query.department}%"))
    if query.role:
        filters.append(User.role.ilike(f"%{query.role}%"))

    db_users = db.query(User)
    if filters:
        logger.debug(f"Applying filters: {filters}")
        db_users = db_users.filter(or_(*filters))
    
    try:
        total = db_users.count()
        users = db_users.offset(skip).limit(limit).all()
        
        if not users:
            logger.warning("No users found matching the search criteria")
            raise HTTPException(status_code=404, detail="No users found")
        
        logger.info(f"Found {len(users)} users out of {total} total matches")
        return users
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") 