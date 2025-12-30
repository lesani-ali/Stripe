from fastapi import FastAPI
from .routes.onboarding import router as onboarding_router
from .routes.checkout import router as checkout_router
from .routes.pages import router as pages_router

app = FastAPI(title="Stripe Connect Test (PaymentIntent)")

app.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
app.include_router(pages_router)

@app.get("/health")
def health():
    return {"ok": True}