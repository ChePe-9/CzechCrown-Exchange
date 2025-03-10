from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..sync import sync_period_data

router = APIRouter()

@router.post("/sync-period")
async def sync_data_for_period(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    sync_period_data(start_date, end_date)
    return {"message": "Data synced successfully"}