# app/schemas/summary.py
from pydantic import BaseModel
from typing import List

class PaperSummary(BaseModel):
    title: str
    contributions: List[str]
    methodology: str
    results: str
    limitations: List[str]
