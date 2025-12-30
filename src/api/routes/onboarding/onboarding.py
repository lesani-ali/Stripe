from fastapi import APIRouter, HTTPException
import stripe

from ...config.config import FRONTEND_URL
from .schema import (CreateConnectedAccountRequest,
                     CreateOnboardingLinkRequest)

router = APIRouter()

@router.post("/connected-account")
def create_connected_account(req: CreateConnectedAccountRequest):
    try:
        payload = dict(
            type="express",
            country=req.country,
            email=req.email,
            capabilities={
                "transfers": {"requested": True},
                "card_payments": {"requested": True},
            },
        )

        if req.manual_payouts:
            payload["settings"] = {"payouts": {"schedule": {"interval": "manual"}}}

        account = stripe.Account.create(**payload)
        return {
            "connected_account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=getattr(e, "user_message", str(e)))



@router.post("/onboarding-link")
def create_onboarding_link(req: CreateOnboardingLinkRequest):
    try:
        link = stripe.AccountLink.create(
            account=req.connected_account_id,
            refresh_url=f"{FRONTEND_URL}/onboarding/refresh",
            return_url=f"{FRONTEND_URL}/onboarding/complete",
            type="account_onboarding",
        )
        return {"url": link.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=getattr(e, "user_message", str(e)))