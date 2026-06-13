from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from datetime import datetime
from collections import defaultdict

app = FastAPI(
    title="Password Strength Analyzer API",
    description="A utility-focused microservice designed to analyze the strength of user passwords based on various criteria including length, character diversity, and common patterns.",
    version="1.0.0"
)

# In-memory rate limit dictionary
RATE_LIMITS = defaultdict(int)

# Dependency function for API key verification and rate limiting
def verify_api_key_and_rate_limit(request: Request, x_api_key: str = Header(None)):
    valid_keys = os.getenv('API_KEYS', '').split(',')
    
    if x_api_key in valid_keys:
        return  # Bypass rate limits
    
    client_ip = request.client.host
    
    # Check and update rate limit for the client IP
    if RATE_LIMITS[client_ip] >= 100:
        raise HTTPException(status_code=402, detail='Rate limit exceeded. To get unlimited access and your API key, subscribe at: https://buy.stripe.com/bJe00kcNzgd1dIz2SL6Na00')
    
    RATE_LIMITS[client_ip] += 1

# Root endpoint to redirect to the interactive documentation
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

# Pydantic model for request body
class PasswordRequest(BaseModel):
    password: str

# Pydantic model for response body
class PasswordResponse(BaseModel):
    strength_score: int
    feedback: list[str]

# Function to evaluate password strength
def evaluate_password_strength(password: str) -> dict:
    score = 0
    feedback = []
    
    # Check length
    if len(password) < 8:
        score += 20
        feedback.append("Your password is too short. Consider using at least 8 characters.")
    else:
        score += 40
    
    # Check character diversity
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if has_upper and has_lower:
        score += 10
    elif has_upper or has_lower:
        score += 5
    
    if has_digit:
        score += 10
    if has_special:
        score += 10
    
    # Feedback on character diversity
    if not (has_upper and has_lower):
        feedback.append("Consider using a mix of uppercase and lowercase letters.")
    if not has_digit:
        feedback.append("Consider including numbers in your password for added security.")
    if not has_special:
        feedback.append("Including special characters can enhance the strength of your password.")
    
    # Check for common patterns
    common_patterns = ["password", "123456", "qwerty"]
    if any(pattern in password.lower() for pattern in common_patterns):
        score -= 20
        feedback.append(f"Avoid using easily guessable patterns like '{[pattern for pattern in common_patterns if pattern in password.lower()][0]}'.")

    return {"strength_score": max(0, score), "feedback": feedback}

# POST endpoint to analyze password strength
@app.post("/analyze", response_model=PasswordResponse, dependencies=[Depends(verify_api_key_and_rate_limit)])
def analyze_password(request: PasswordRequest):
    result = evaluate_password_strength(request.password)
    return result

# Run the application using Uvicorn
