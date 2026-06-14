# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse

app = FastAPI(title="GDPR Data Retention Lifespan Engine")

class EvaluationRequest(BaseModel):
    data_category: str
    creation_date: str
    current_date: str

RETENTION_PERIODS = {
    "marketing": 3,
    "financial": 7
}

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs", status_code=307)

@app.post("/evaluate", response_model=dict)
async def evaluate_retention_period(request: EvaluationRequest):
    try:
        creation_date = datetime.strptime(request.creation_date, "%Y-%m-%d")
        current_date = datetime.strptime(request.current_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD.")
    
    retention_years = RETENTION_PERIODS.get(request.data_category)
    if retention_years is None:
        raise HTTPException(status_code=400, detail=f"Unsupported data category: {request.data_category}. Supported categories are: {', '.join(RETENTION_PERIODS.keys())}")
    
    retention_end_date = creation_date + timedelta(days=retention_years * 365)
    days_remaining = (retention_end_date - current_date).days
    cleanup_flag = current_date > retention_end_date
    
    return {
        "retention_years": retention_years,
        "days_remaining": max(days_remaining, 0),
        "cleanup_flag": cleanup_flag
    }