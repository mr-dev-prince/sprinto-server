from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from app.services.user_service import create_user_from_clerk, update_user_from_clerk, deactivate_user_from_clerk

router = APIRouter()

@router.get("/")
async def healt_check():
    return {"is_webhook_api_healthy": True}

@router.post("/clerk")
async def create_user(request : Request, db: AsyncSession = Depends(get_db)):
    payload = await request.json()
    event_type = payload.get("type")
    data = payload.get("data")

    if not event_type or not data:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if event_type == "user.created":
        await create_user_from_clerk(db, data)

    elif event_type == "user.updated":
        await update_user_from_clerk(db, data)

    elif event_type == "user.deleted":
        await deactivate_user_from_clerk(db, data)

    return {"ok": True}