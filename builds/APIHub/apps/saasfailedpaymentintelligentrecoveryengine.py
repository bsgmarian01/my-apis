from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
import math

app = FastAPI(title="SaaS Failed Payment Intelligent Recovery Engine")

@app.get("/")
async def root():
    return {"message": "200 OK"}

@app.post("/optimize-retry")
async def optimize_retry(request: Request):
    data = await request.json()
    
    failed_date = datetime.strptime(data['failed_date'], '%Y-%m-%d')
    failure_reason = data['failure_reason']
    customer_timezone = data['customer_timezone']
    amount = data['amount']

    # Example logic to determine optimal_retry_date, action_channel, and urgency_score
    if failure_reason == 'insufficient_funds':
        optimal_retry_date = failed_date + timedelta(days=7)
        action_channel = 'email_update_form'
        urgency_score = 3
    elif failure_reason == 'expired_card':
        optimal_retry_date = failed_date + timedelta(days=2)
        action_channel = 'delayed_retry'
        urgency_score = 4
    else:
        optimal_retry_date = failed_date + timedelta(days=5)
        action_channel = 'email_update_form'
        urgency_score = 2

    return {
        "optimal_retry_date": optimal_retry_date.strftime('%Y-%m-%d'),
        "action_channel": action_channel,
        "urgency_score": urgency_score
    }

@app.get("/docs", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")