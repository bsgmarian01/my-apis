from fastapi import FastAPI, Request, Depends, HTTPException, Header
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import os
from datetime import date

app = FastAPI(
    title="Credit Card Validator API",
    description="This API provides a simple utility to validate the format and checksum of credit card numbers using the Luhn algorithm. It supports various card types including Visa, MasterCard, American Express, Discover, JCB, and Diners Club."
)

# In-memory rate limit storage


class CreditCardRequest(BaseModel):
    """
    Pydantic model for the request body of credit card validation.
    
    Attributes:
        card_number (str): The credit card number to be validated.
    """
    card_number: str

class CreditCardResponse(BaseModel):
    """
    Pydantic model for the response body of credit card validation.
    
    Attributes:
        is_valid (bool): Indicates whether the card number is valid.
        card_type (str): The type of the credit card if valid, otherwise 'Unknown'.
        message (str): A descriptive message about the validation result.
    """
    is_valid: bool
    card_type: str
    message: str

def luhn_check(card_number: str) -> bool:
    """
    Validates a credit card number using the Luhn algorithm.

    Args:
        card_number (str): The credit card number to validate.

    Returns:
        bool: True if the card number is valid, False otherwise.
    """
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

def identify_card_type(card_number: str) -> str:
    """
    Identifies the type of credit card based on its prefix.

    Args:
        card_number (str): The credit card number to identify.

    Returns:
        str: The card type if recognized, otherwise 'Unknown'.
    """
    if card_number.startswith(('4',)):
        return "Visa"
    elif card_number.startswith(('51', '52', '53', '54', '55')):
        return "MasterCard"
    elif card_number.startswith(('34', '37')):
        return "American Express"
    elif card_number.startswith(('6011', '65', '644', '645', '646', '647', '648', '649')):
        return "Discover"
    elif card_number.startswith(('3528', '3529', '353', '354', '355', '356', '357', '358')):
        return "JCB"
    elif card_number.startswith(('300', '301', '302', '303', '304', '305', '36', '38')):
        return "Diners Club"
    else:
        return "Unknown"

@app.get('/', include_in_schema=False)
def root():
    """
    Redirects to the interactive documentation.
    
    Returns:
        RedirectResponse: A redirect response to /docs.
    """
    return RedirectResponse(url='/docs')

@app.post('/validate', response_model=CreditCardResponse)
def validate_credit_card(request_body: CreditCardRequest) -> CreditCardResponse:
    """
    Validates a credit card number using the Luhn algorithm and identifies its type.

    Args:
        request_body (CreditCardRequest): The request body containing the credit card number to validate.

    Returns:
        CreditCardResponse: A response indicating whether the card is valid, its type, and a message.
    """
    card_number = request_body.card_number.replace(" ", "")
    
    if not card_number.isdigit():
        return CreditCardResponse(is_valid=False, card_type="Unknown", message="Invalid input. The card number should contain only digits.")
    
    is_valid = luhn_check(card_number)
    card_type = identify_card_type(card_number) if is_valid else "Unknown"
    
    if is_valid:
        message = f"The card number is valid and belongs to {card_type}."
    else:
        message = "The card number is invalid."
    
    return CreditCardResponse(is_valid=is_valid, card_type=card_type, message=message)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)