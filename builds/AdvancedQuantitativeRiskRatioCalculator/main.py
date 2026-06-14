from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import math
from pydantic import BaseModel

app = FastAPI(title="Advanced Quantitative Risk Ratio Calculator")

class RiskRequest(BaseModel):
    daily_returns: list[float]
    risk_free_rate: float

@app.get("/", status_code=200)
def root():
    return {"message": "OK"}

@app.post("/risk-ratios", response_model=dict)
def calculate_risk_ratios(request: RiskRequest):
    daily_returns = request.daily_returns
    risk_free_rate = request.risk_free_rate

    if not daily_returns:
        raise HTTPException(status_code=400, detail=[{"loc": ["body", "daily_returns"], "msg": "daily_returns must not be empty", "type": "value_error"}])

    mean_return = sum(daily_returns) / len(daily_returns)

    # Calculate standard deviation (volatility)
    variance = sum((x - mean_return) ** 2 for x in daily_returns) / len(daily_returns)
    if variance == 0:
        raise HTTPException(status_code=400, detail=[{"loc": ["body", "daily_returns"], "msg": "Daily returns have no variation", "type": "value_error"}])

    volatility = math.sqrt(variance)

    # Calculate Sharpe Ratio
    sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility != 0 else float('inf')

    # Calculate Sortino Ratio (assuming downside deviation)
    downside_returns = [x for x in daily_returns if x < mean_return]
    downside_variance = sum((x - mean_return) ** 2 for x in downside_returns) / len(daily_returns) if downside_returns else 0
    downside_volatility = math.sqrt(downside_variance)

    sortino_ratio = (mean_return - risk_free_rate) / downside_volatility if downside_volatility != 0 else float('inf')

    # Calculate Calmar Ratio (assuming maximum drawdown is the minimum cumulative return)
    cumulative_returns = [1]
    for ret in daily_returns:
        cumulative_returns.append(cumulative_returns[-1] * (1 + ret))

    max_drawdown = min(cumulative_returns) - 1

    calmar_ratio = mean_return / abs(max_drawdown) if max_drawdown != 0 else float('inf') if max_drawdown == 0 and mean_return > 0 else None

    return {
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "calmar_ratio": calmar_ratio
    }