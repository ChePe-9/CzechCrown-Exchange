from pydantic import BaseModel
from typing import List

class Rate(BaseModel):
    date: str
    currency: str
    rate: float

class ReportResponse(BaseModel):
    currency: str
    min_rate: float
    max_rate: float
    avg_rate: float