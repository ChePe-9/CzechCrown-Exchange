from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db, ExchangeRate
from ..models import ReportResponse
from ..logging_config import logger  # Импортируем логгер

router = APIRouter()

@router.get("/report", response_model=List[ReportResponse])
async def get_report(
    start_date: str,
    end_date: str,
    currencies: List[str] = Query(default=...),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching report for currencies: {currencies}, period: {start_date} - {end_date}")
    results = []
    for currency in currencies:
        rates = (
            db.query(ExchangeRate.rate)
            .filter(
                ExchangeRate.currency == currency,
                ExchangeRate.date >= start_date,
                ExchangeRate.date <= end_date
            )
            .all()
        )
        if not rates:
            logger.warning(f"No data found for currency: {currency}")
            raise HTTPException(status_code=404, detail=f"No data found for {currency}")
        rates = [rate[0] for rate in rates]
        results.append(
            ReportResponse(
                currency=currency,
                min_rate=min(rates),
                max_rate=max(rates),
                avg_rate=sum(rates) / len(rates)
            )
        )
    logger.info(f"Report generated successfully for currencies: {currencies}")
    return results