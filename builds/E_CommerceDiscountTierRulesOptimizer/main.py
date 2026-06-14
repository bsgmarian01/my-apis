from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="E-Commerce Discount Tier Rules Optimizer")

class CartItem(BaseModel):
    cart_total: float
    active_promos: list[dict]

@app.post("/discount-apply", response_model=dict)
def apply_discount(cart_item: CartItem):
    best_promo_applied = None
    discount_amount = 0.0
    final_total = cart_item.cart_total

    for promo in cart_item.active_promos:
        threshold = promo.get('threshold', 0)
        discount_pct = promo.get('discount_pct', 0)

        if cart_item.cart_total >= threshold:
            current_discount = (discount_pct / 100) * cart_item.cart_total
            if current_discount > discount_amount:
                best_promo_applied = promo
                discount_amount = current_discount

    final_total -= discount_amount
    best_promo_name = best_promo_applied.get('name', 'No Promo') if best_promo_applied else 'No Promo'

    return {
        "best_promo_applied": best_promo_name,
        "discount_amount": discount_amount,
        "final_total": final_total
    }

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)