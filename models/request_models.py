from pydantic import BaseModel
from typing import Optional

class PredictionRequest(BaseModel):
    user_id: int
    product_code: str
    start_date: str
    end_date: str
    campaign: Optional[int] = None

class CategoryPredictionRequest(BaseModel):
    start_date: str
    end_date: str
    user_id: Optional[int] = None